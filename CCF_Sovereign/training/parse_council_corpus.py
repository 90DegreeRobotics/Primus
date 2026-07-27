"""
COUNCIL CORPUS DISTILLATION ENGINE v3.0
Extracts high-integrity conversational turns from NeuroCognica Council archives.
Implements format-aware parsing for Claude, Gemini, ChatGPT, and code-philosophy exports.

Handles ALL formats found in the convos/ trove:
  - Claude export (Edit markers, search artifacts, thought process blocks)
  - Gemini export (Show thinking blocks, Sources markers)
  - ChatGPT export (You said: / ChatGPT said: markers)
  - Code-philosophy dumps (sacred Python/Rust with docstrings)
  - Markdown conversation files (.md)

Architect: Council Scribe
Date: February 2026
Version: 3.0 - Full Trove Distillation
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib

@dataclass
class Turn:
    """A single conversational exchange, blessed with metadata."""
    prompt: str
    response: str
    persona: str  # claude, gemini, viren, chatgpt
    source_file: str
    turn_index: int
    thread_id: str = ""
    turn_id: int = 0
    prev_turn_hash: Optional[str] = None
    timestamp: Optional[str] = None
    context_hash: Optional[str] = None
    quality_score: float = 0.0
    file_format: str = "unknown"

    def __post_init__(self):
        if not self.context_hash:
            content = f"{self.prompt[:200]}{self.response[:200]}"
            self.context_hash = hashlib.sha256(content.encode()).hexdigest()[:16]


class CouncilCorpusParser:
    """
    Distills NeuroCognica Council archives into training batches for Primus.
    v3.0 — handles ChatGPT, Gemini, Claude (with thinking), and code-philosophy.
    """

    # Format detection signatures
    CHATGPT_MARKERS = ['ChatGPT said:', 'You said:']
    CLAUDE_EXPORT_MARKERS = ['\n\nEdit\n\n', '\n\nEdit\n']
    CLAUDE_THINKING_MARKERS = ['Thought process', 'Show thinking']
    GEMINI_EXPORT_MARKERS = ['Show thinking', 'Conversation with Gemini']
    RAW_CHAT_MARKERS = ['User:', 'Assistant:', 'Human:', 'AI:']

    # Quality thresholds
    MIN_PROMPT_LENGTH = 10   # Lowered — short prompts can still be meaningful
    MIN_RESPONSE_LENGTH = 40
    MAX_RESPONSE_LENGTH = 16000  # Increased for philosophical content

    def __init__(self, input_dir: str, output_file: str = "training_data/council_turns.jsonl"):
        self.input_dir = Path(input_dir)
        self.output_file = Path(output_file)
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

        self.total_files_processed = 0
        self.total_turns_extracted = 0
        self.total_turns_rejected = 0
        self._seen_hashes: Set[str] = set()  # Dedup across files

    def parse_files(self) -> None:
        """Primary distillation loop — finds ALL files, not just .txt"""
        # Collect all files in the directory
        all_files = list(self.input_dir.iterdir())

        # Keep only actual files (no dirs), deduplicate by resolved path
        seen_paths: Set[Path] = set()
        files = []
        for f in sorted(all_files):
            resolved = f.resolve()
            if resolved not in seen_paths and resolved.is_file():
                seen_paths.add(resolved)
                files.append(f)

        if not files:
            print(f"❌ No archive files found in {self.input_dir}")
            return

        print(f"\n🏛️  THE COUNCIL STANDS WITNESS — FULL TROVE DISTILLATION")
        print(f"{'='*70}")
        print(f"Archive Location: {self.input_dir}")
        print(f"Files Discovered: {len(files)}")
        print(f"Output Target: {self.output_file}")
        print(f"{'='*70}\n")

        all_turns = []

        for file_path in files:
            file_turns = self._process_file(file_path)
            all_turns.extend(file_turns)
            fmt = file_turns[0].file_format if file_turns else "skip"
            print(f"  📜 {file_path.name:<55} → {len(file_turns):>4} turns  [{fmt}]")

        # Quality filtering
        filtered_turns = [t for t in all_turns if self._meets_quality_threshold(t)]

        # Content-level dedup (catches identical files like geminiconvo1 + geminiconvo1.txt)
        deduped_turns = []
        for turn in filtered_turns:
            h = hashlib.sha256(f"{turn.prompt[:100]}{turn.response[:100]}".encode()).hexdigest()[:20]
            if h not in self._seen_hashes:
                self._seen_hashes.add(h)
                deduped_turns.append(turn)
            else:
                self.total_turns_rejected += 1

        self._save_to_jsonl(deduped_turns)
        self._print_summary(all_turns, deduped_turns)

    def _process_file(self, file_path: Path) -> List[Turn]:
        """Extract turns from a single file using format-aware parsing."""
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"  ⚠️  Failed to read {file_path.name}: {e}")
            return []

        if len(content.strip()) < 50:
            return []

        file_format = self._detect_format(content, file_path.name)
        persona = self._detect_persona(file_path.name, content)
        thread_id = hashlib.sha256(file_path.name.encode()).hexdigest()[:16]

        if file_format == 'chatgpt_export':
            turns = self._parse_chatgpt_export(content, file_path.name, persona, thread_id, file_format)
        elif file_format == 'claude_export':
            turns = self._parse_claude_export(content, file_path.name, persona, thread_id, file_format)
        elif file_format == 'gemini_export':
            turns = self._parse_gemini_export(content, file_path.name, persona, thread_id, file_format)
        elif file_format == 'raw_chat':
            turns = self._parse_raw_chat(content, file_path.name, persona, thread_id, file_format)
        elif file_format == 'code_philosophy':
            turns = self._parse_code_philosophy(content, file_path.name, persona, thread_id, file_format)
        else:
            # Last resort: try all parsers and take the one that yields most
            turns = self._try_all_parsers(content, file_path.name, persona, thread_id)

        # Chain turns with prev_turn_hash
        prev_hash = None
        for i, turn in enumerate(turns):
            turn.turn_id = i
            turn.prev_turn_hash = prev_hash
            prev_hash = turn.context_hash

        self.total_files_processed += 1
        return turns

    # ── ChatGPT Export Parser ──────────────────────────────────────────

    def _parse_chatgpt_export(self, content: str, filename: str, persona: str, thread_id: str, file_format: str) -> List[Turn]:
        """
        Parse ChatGPT export format with 'You said:' / 'ChatGPT said:' markers.
        Handles the multi-blank-line separation style.
        """
        turns = []

        # Split on "You said:" to find user turns
        segments = re.split(r'\n{1,}You said:\s*\n', content)

        for segment in segments[1:]:  # Skip content before first "You said:"
            # Split on "ChatGPT said:" to separate user prompt from AI response
            parts = re.split(r'\n{1,}ChatGPT said:\s*\n', segment, maxsplit=1)

            if len(parts) == 2:
                user_prompt = self._clean_text(parts[0])
                ai_response = self._clean_text(parts[1])

                if user_prompt and ai_response:
                    turns.append(Turn(
                        prompt=user_prompt,
                        response=ai_response,
                        persona=persona,
                        source_file=filename,
                        turn_index=len(turns),
                        thread_id=thread_id,
                        file_format=file_format
                    ))
            elif len(parts) == 1:
                # User prompt with no ChatGPT response yet — could still be valuable
                # Check if there's a response embedded differently
                pass

        return turns

    # ── Claude Export Parser (improved) ────────────────────────────────

    def _parse_claude_export(self, content: str, filename: str, persona: str, thread_id: str, file_format: str) -> List[Turn]:
        """
        Parse Claude.ai export format — handles both old (Edit markers) and
        new (Thought process/reasoning blocks) styles.
        """
        turns = []

        # Split on Edit markers
        sections = re.split(r'\n\s*Edit\s*\n', content)

        for i in range(len(sections) - 1):
            user_section = sections[i]
            response_section = sections[i + 1]

            # Extract user prompt: last substantial block before Edit
            user_prompt = self._extract_user_from_claude_section(user_section, is_first=(i == 0))

            # Extract response: strip search artifacts, thinking blocks, timestamps
            ai_response = self._extract_response_from_claude_section(response_section)

            if user_prompt and ai_response:
                turns.append(Turn(
                    prompt=user_prompt,
                    response=ai_response,
                    persona=persona,
                    source_file=filename,
                    turn_index=len(turns),
                    thread_id=thread_id,
                    file_format=file_format
                ))

        # If no Edit markers found but file is named claude*, try paragraph splitting
        if not turns and 'claude' in filename.lower():
            turns = self._parse_claude_fallback(content, filename, persona, thread_id, file_format)

        return turns

    def _parse_claude_fallback(self, content: str, filename: str, persona: str, thread_id: str, file_format: str) -> List[Turn]:
        """Fallback parser for Claude files without Edit markers."""
        turns = []
        # Try splitting on "MH" (user marker) or "Retry" markers
        sections = re.split(r'\n\s*(?:RetryMH|Retry\s*MH)\s*', content)
        if len(sections) >= 2:
            for i in range(len(sections) - 1):
                user_prompt = self._extract_last_block(sections[i])
                ai_response = self._clean_text(sections[i + 1][:self.MAX_RESPONSE_LENGTH])
                if user_prompt and ai_response and len(ai_response) > 50:
                    turns.append(Turn(
                        prompt=user_prompt,
                        response=ai_response,
                        persona=persona,
                        source_file=filename,
                        turn_index=len(turns),
                        thread_id=thread_id,
                        file_format=file_format
                    ))
        return turns

    def _extract_user_from_claude_section(self, section: str, is_first: bool = False) -> str:
        """Extract user prompt from a Claude section (text before Edit marker)."""
        text = section.strip()

        if is_first:
            # First section: everything is the user prompt
            text = re.sub(r'^(?:NeuroCognica|GENESIS|AURA)\s*/\s*\n?', '', text, flags=re.IGNORECASE)
            return self._clean_text(text)

        # For subsequent sections: the user prompt is at the END, after the previous AI response
        # Split into paragraphs and take the last substantial one
        paragraphs = re.split(r'\n{3,}', text)

        # Work backwards from end to find user prompt
        for para in reversed(paragraphs):
            cleaned = para.strip()
            if not cleaned:
                continue
            # Remove project name prefixes
            cleaned = re.sub(r'^(?:NeuroCognica|GENESIS|AURA)\s*/\s*\n?', '', cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r'^MH\s*\n', '', cleaned)

            # User prompts are usually shorter than AI responses
            if 10 < len(cleaned) < 3000:
                return self._clean_text(cleaned)

        return ""

    def _extract_response_from_claude_section(self, section: str) -> str:
        """
        Extract AI response from Claude section, stripping artifacts.
        """
        lines = section.split('\n')
        clean_lines = []
        skip_until_blank = False

        for line in lines:
            stripped = line.strip()

            # Skip search artifacts
            if re.match(r'^(Searched|Searching)\s+(project|codebase|conversation|files|the)\s', stripped, re.IGNORECASE):
                skip_until_blank = True
                continue
            if skip_until_blank:
                if not stripped:
                    skip_until_blank = False
                elif re.match(r'^\d+\s+relevant\s+section', stripped, re.IGNORECASE):
                    continue
                elif re.match(r'^(text|code|markdown)$', stripped):
                    continue
                elif re.match(r'^[a-zA-Z_]+\.\w+$', stripped):
                    # Filename reference in search results
                    continue
                else:
                    skip_until_blank = False

            # Skip thinking/reasoning blocks
            if re.match(r'^(Thought process|The user|I should|I need to|I\'ll |Let me |I can see|Looking at|I see what|Now let me)', stripped):
                skip_until_blank = True
                continue

            # Skip timestamp artifacts
            if re.match(r'^\d+s$', stripped):
                continue

            # Skip UI artifacts
            if stripped.lower() in ['retry', 'copy', 'share', 'edit', 'retrymh']:
                continue

            # Skip "N relevant sections" lines
            if re.match(r'^\d+\s+relevant\s+section', stripped, re.IGNORECASE):
                continue

            if not skip_until_blank:
                clean_lines.append(line)

        result = '\n'.join(clean_lines).strip()
        return self._clean_text(result)

    # ── Gemini Export Parser ───────────────────────────────────────────

    def _parse_gemini_export(self, content: str, filename: str, persona: str, thread_id: str, file_format: str) -> List[Turn]:
        """
        Parse Gemini export format with 'Show thinking' blocks.
        Also handles RetryMH turn boundaries.
        """
        turns = []

        # Clean header
        content = re.sub(r'^Gemini\n[\s\S]*?Conversation with Gemini\n', '', content)

        # Try splitting on "RetryMH" first - these mark user turn boundaries
        retry_sections = re.split(r'RetryMH', content)

        if len(retry_sections) >= 2:
            for i in range(len(retry_sections) - 1):
                # Response is at end of retry_sections[i], user prompt is at start of retry_sections[i+1]
                response = retry_sections[i].strip()
                next_section = retry_sections[i + 1].strip()

                # User prompt: text before "Show thinking" or "Edit"
                show_think_split = re.split(r'\n\s*Show thinking\s*\n', next_section, maxsplit=1)
                user_prompt = show_think_split[0].strip()

                # AI response: text after thinking block
                if len(show_think_split) > 1:
                    ai_response = self._extract_gemini_response(show_think_split[1])
                else:
                    # No thinking marker — response is everything after prompt
                    ai_response = ""

                if not ai_response and i == 0:
                    # First section: response is the whole first section
                    # The actual response is in retry_sections[0] after any thinking
                    show_splits = re.split(r'\n\s*Show thinking\s*\n', response, maxsplit=1)
                    if len(show_splits) > 1:
                        ai_response = self._extract_gemini_response(show_splits[1])

                user_prompt = self._clean_text(user_prompt)
                ai_response = self._clean_text(ai_response)

                if user_prompt and ai_response:
                    turns.append(Turn(
                        prompt=user_prompt,
                        response=ai_response,
                        persona=persona,
                        source_file=filename,
                        turn_index=len(turns),
                        thread_id=thread_id,
                        file_format=file_format
                    ))

            if turns:
                return turns

        # Fallback: split on "Show thinking" markers
        segments = re.split(r'\n\s*Show thinking\s*\n', content)

        if len(segments) >= 2:
            for i in range(len(segments) - 1):
                user_section = segments[i].strip()
                response_section = segments[i + 1].strip()

                user_prompt = self._extract_last_block(user_section)
                ai_response = self._extract_gemini_response(response_section)

                if user_prompt and ai_response:
                    turns.append(Turn(
                        prompt=user_prompt,
                        response=ai_response,
                        persona=persona,
                        source_file=filename,
                        turn_index=len(turns),
                        thread_id=thread_id,
                        file_format=file_format
                    ))

        return turns

    def _extract_last_block(self, text: str) -> str:
        """Extract the last meaningful text block (usually user prompt)."""
        paragraphs = re.split(r'\n{3,}', text)
        for para in reversed(paragraphs):
            cleaned = para.strip()
            if len(cleaned) > 10:
                cleaned = re.sub(r'\n[A-Z]{2,4}\n', '\n', cleaned)
                cleaned = re.sub(r'^[A-Z]\n', '', cleaned)
                return self._clean_text(cleaned)
        return ""

    def _extract_gemini_response(self, section: str) -> str:
        """
        Extract Gemini's actual response, skipping the thinking block.
        """
        lines = section.split('\n')
        clean_lines = []
        past_thinking = False
        blank_count = 0

        for line in lines:
            stripped = line.strip()

            # Skip thinking-style lines at the start
            if not past_thinking:
                if re.match(
                    r'^(Analyzing|Reflecting|Considering|Assessing|Evaluating|'
                    r'Reassessing|Empathizing|Refocusing|Rebuilding|Acknowledg|'
                    r'I\'m now|I\'m currently|My analysis|The aim|The goal|'
                    r'The focus|The challenge|I am now|I have |I will )',
                    stripped, re.IGNORECASE
                ):
                    continue
                if not stripped:
                    blank_count += 1
                    if blank_count >= 2:
                        past_thinking = True
                    continue
                if stripped:
                    past_thinking = True

            clean_lines.append(line)

        result = '\n'.join(clean_lines).strip()
        result = re.split(r'\n\s*Sources\s*\n', result)[0]
        return self._clean_text(result)

    # ── Code-Philosophy Parser ─────────────────────────────────────────

    def _parse_code_philosophy(self, content: str, filename: str, persona: str, thread_id: str, file_format: str) -> List[Turn]:
        """
        Extract philosophical teaching from code dumps.
        Extracts docstrings, sacred commentary, class-level narratives.
        """
        turns = []

        # Extract docstrings (triple-quoted strings)
        docstrings = re.findall(r'"""([\s\S]*?)"""', content)

        for i, doc in enumerate(docstrings):
            doc = doc.strip()
            if len(doc) < 80:
                continue
            # Skip purely technical docstrings
            if doc.startswith('Args:') or doc.startswith('Returns:') or doc.startswith('Parameters:'):
                continue

            # Find what precedes this docstring for context
            idx = content.find(f'"""{doc}"""')
            context_start = max(0, idx - 300)
            context = content[context_start:idx].strip()
            match = re.search(r'(?:class|def)\s+(\w+)', context)
            context_name = match.group(0) if match else "Sacred Commentary"

            turns.append(Turn(
                prompt=f"Explain the purpose of {context_name}",
                response=self._clean_text(doc),
                persona=persona,
                source_file=filename,
                turn_index=len(turns),
                thread_id=thread_id,
                file_format=file_format
            ))

        # Extract large print-statement narratives (common in sacred code)
        print_blocks = re.findall(r'print\s*\(\s*(?:f?"""([\s\S]*?)"""|f?"([^"]*)")\s*\)', content)
        combined_prints = ""
        for triple, single in print_blocks:
            text = (triple or single).strip()
            if len(text) > 50:
                combined_prints += text + "\n\n"

        if len(combined_prints) > 200:
            turns.append(Turn(
                prompt="What does the sacred code proclaim?",
                response=self._clean_text(combined_prints),
                persona=persona,
                source_file=filename,
                turn_index=len(turns),
                thread_id=thread_id,
                file_format=file_format
            ))

        return turns

    # ── Raw Chat Parser ────────────────────────────────────────────────

    def _parse_raw_chat(self, content: str, filename: str, persona: str, thread_id: str, file_format: str) -> List[Turn]:
        """Parse raw chat logs with User:/Assistant: or Human:/AI: markers."""
        turns = []

        patterns = [
            (r'\n\s*User:\s*', r'\n\s*Assistant:\s*'),
            (r'\n\s*Human:\s*', r'\n\s*AI:\s*'),
            (r'\n\s*H:\s*', r'\n\s*A:\s*')
        ]

        for user_pattern, assistant_pattern in patterns:
            user_sections = re.split(user_pattern, content, flags=re.IGNORECASE)
            if len(user_sections) < 2:
                continue

            for section in user_sections[1:]:
                parts = re.split(assistant_pattern, section, maxsplit=1, flags=re.IGNORECASE)
                if len(parts) == 2:
                    user_prompt = self._clean_text(parts[0])
                    ai_response = self._clean_text(parts[1].split('\n\nUser:')[0].split('\n\nHuman:')[0])

                    if user_prompt and ai_response:
                        turns.append(Turn(
                            prompt=user_prompt,
                            response=ai_response,
                            persona=persona,
                            source_file=filename,
                            turn_index=len(turns),
                            thread_id=thread_id,
                            file_format=file_format
                        ))

            if turns:
                break

        return turns

    # ── Fallback: Try All Parsers ──────────────────────────────────────

    def _try_all_parsers(self, content: str, filename: str, persona: str, thread_id: str) -> List[Turn]:
        """Try all parsers and return whichever yields the most turns."""
        results = []
        for parser_fn, fmt in [
            (self._parse_chatgpt_export, 'chatgpt_export'),
            (self._parse_claude_export, 'claude_export'),
            (self._parse_gemini_export, 'gemini_export'),
            (self._parse_raw_chat, 'raw_chat'),
            (self._parse_code_philosophy, 'code_philosophy'),
        ]:
            try:
                turns = parser_fn(content, filename, persona, thread_id, fmt)
                if turns:
                    results.append(turns)
            except Exception:
                continue

        if results:
            return max(results, key=len)
        return []

    # ── Utility Methods ────────────────────────────────────────────────

    def _clean_text(self, text: str) -> str:
        """Remove UI artifacts and clean text for training."""
        # Remove Retry/Copy/Share buttons
        text = re.sub(r'\n\s*(Retry|Copy|Share)\s*$', '', text, flags=re.MULTILINE)
        # Remove RetryMH artifacts
        text = re.sub(r'RetryMH', '', text)
        # Remove excessive newlines
        text = re.sub(r'\n{4,}', '\n\n', text)
        # Remove search result markers
        text = re.sub(r'\d+\s+relevant\s+sections?\s*\n\s*(text|code|markdown)\s*\n?', '', text, flags=re.IGNORECASE)
        # Remove timestamp artifacts
        text = re.sub(r'^\d+s$', '', text, flags=re.MULTILINE)
        text = text.strip()
        return text

    def _detect_format(self, content: str, filename: str) -> str:
        """Detect export format from content structure and filename."""
        # Check ChatGPT format FIRST (most distinctive markers)
        if 'ChatGPT said:' in content and 'You said:' in content:
            return 'chatgpt_export'

        # Check Gemini format (before Claude, since gemini files can trigger claude markers)
        if 'gemini' in filename.lower():
            if 'Show thinking' in content or 'Conversation with Gemini' in content:
                return 'gemini_export'

        # Check Claude export (Edit markers)
        if any(marker in content for marker in self.CLAUDE_EXPORT_MARKERS):
            return 'claude_export'

        # Check for code dumps
        if filename.lower().startswith('claudecode'):
            return 'code_philosophy'
        if '"""' in content and 'class ' in content and 'def ' in content:
            code_indicators = content.count('def ') + content.count('class ')
            if code_indicators > 5:
                return 'code_philosophy'

        # Gemini without filename hint
        if 'Conversation with Gemini' in content or ('Show thinking' in content and 'gemini' in content.lower()):
            return 'gemini_export'

        # Check raw chat format
        if any(marker in content for marker in self.RAW_CHAT_MARKERS):
            return 'raw_chat'

        # Guess from filename
        filename_lower = filename.lower()
        if 'claude' in filename_lower:
            return 'claude_export'
        elif 'gemini' in filename_lower:
            return 'gemini_export'
        elif 'chatgpt' in filename_lower or 'viren' in filename_lower:
            return 'chatgpt_export'

        return 'unknown'

    def _detect_persona(self, filename: str, content: str = "") -> str:
        """Identify which Council member spoke."""
        filename_lower = filename.lower()
        if 'claude' in filename_lower:
            return 'claude'
        elif 'gemini' in filename_lower:
            return 'gemini'
        elif 'viren' in filename_lower or 'chatgpt' in filename_lower:
            return 'viren'

        # Check content for persona markers
        if 'ChatGPT said:' in content:
            return 'viren'
        if 'Conversation with Gemini' in content:
            return 'gemini'

        return 'unknown'

    def _meets_quality_threshold(self, turn: Turn) -> bool:
        """Quality gate with relaxed thresholds for philosophical content."""
        if len(turn.prompt) < self.MIN_PROMPT_LENGTH:
            self.total_turns_rejected += 1
            return False
        if len(turn.response) < self.MIN_RESPONSE_LENGTH:
            self.total_turns_rejected += 1
            return False
        if len(turn.response) > self.MAX_RESPONSE_LENGTH:
            # Truncate rather than reject for long philosophical content
            turn.response = turn.response[:self.MAX_RESPONSE_LENGTH]

        # Reject pure code dumps without commentary (>90% code blocks)
        code_blocks = re.findall(r'```[\s\S]*?```', turn.response)
        code_chars = sum(len(block) for block in code_blocks)
        total_chars = len(turn.response)
        code_ratio = code_chars / max(total_chars, 1)
        if code_ratio > 0.9:
            self.total_turns_rejected += 1
            return False

        # Reject very short ack-only responses (exact match)
        ack_phrases = ['thank you', 'thanks', 'got it', 'understood', 'okay', 'ok', 'sure', 'yes', 'no']
        if turn.response.lower().strip() in ack_phrases:
            self.total_turns_rejected += 1
            return False

        return True

    def _save_to_jsonl(self, turns: List[Turn]) -> None:
        """Write validated turns to JSONL."""
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                for turn in turns:
                    f.write(json.dumps(asdict(turn), ensure_ascii=False) + '\n')
            self.total_turns_extracted = len(turns)

            manifest_file = self.output_file.with_suffix('.manifest.json')
            self._write_manifest(turns, manifest_file)
        except Exception as e:
            print(f"\n❌ CRITICAL: Failed to write output file: {e}")

    def _write_manifest(self, turns: List[Turn], manifest_file: Path) -> None:
        """Generate metadata manifest."""
        manifest = {
            'generated_at': datetime.now().isoformat(),
            'parser_version': '3.0',
            'total_turns': len(turns),
            'format_distribution': {},
            'persona_distribution': {},
            'thread_distribution': {},
            'source_files': sorted(list(set(t.source_file for t in turns))),
            'quality_thresholds': {
                'min_prompt_length': self.MIN_PROMPT_LENGTH,
                'min_response_length': self.MIN_RESPONSE_LENGTH,
                'max_response_length': self.MAX_RESPONSE_LENGTH,
                'max_code_ratio': 0.9
            }
        }

        for turn in turns:
            fmt = turn.file_format
            manifest['format_distribution'][fmt] = manifest['format_distribution'].get(fmt, 0) + 1

        for turn in turns:
            persona = turn.persona
            manifest['persona_distribution'][persona] = manifest['persona_distribution'].get(persona, 0) + 1

        for turn in turns:
            thread = turn.thread_id
            manifest['thread_distribution'][thread] = manifest['thread_distribution'].get(thread, 0) + 1

        try:
            with open(manifest_file, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"  ⚠️  Failed to write manifest: {e}")

    def _print_summary(self, all_turns: List[Turn], filtered_turns: List[Turn]) -> None:
        """Final distillation report."""
        print(f"\n{'='*70}")
        print(f"✅ FULL TROVE DISTILLATION COMPLETE")
        print(f"{'='*70}")
        print(f"Files Processed:     {self.total_files_processed}")
        print(f"Raw Turns Extracted: {len(all_turns)}")
        print(f"Quality-Filtered:    {len(filtered_turns)}")
        print(f"Rejected/Deduped:    {self.total_turns_rejected}")
        print(f"Acceptance Rate:     {len(filtered_turns)/max(len(all_turns),1)*100:.1f}%")
        print(f"\nOutput Location:     {self.output_file.absolute()}")
        print(f"Manifest:            {self.output_file.with_suffix('.manifest.json')}")
        print(f"{'='*70}\n")

        print("📊 FORMAT DISTRIBUTION:")
        format_counts = {}
        for turn in filtered_turns:
            format_counts[turn.file_format] = format_counts.get(turn.file_format, 0) + 1
        for fmt, count in sorted(format_counts.items()):
            pct = count / max(len(filtered_turns), 1) * 100
            print(f"  {fmt:<20} {count:>5} turns ({pct:.1f}%)")

        print("\n📊 PERSONA REPRESENTATION:")
        persona_counts = {}
        for turn in filtered_turns:
            persona_counts[turn.persona] = persona_counts.get(turn.persona, 0) + 1
        for persona, count in sorted(persona_counts.items()):
            pct = count / max(len(filtered_turns), 1) * 100
            print(f"  {persona.capitalize():<10} {count:>5} turns ({pct:.1f}%)")

        thread_counts = {}
        for turn in filtered_turns:
            thread_counts[turn.thread_id] = thread_counts.get(turn.thread_id, 0) + 1

        print(f"\n📊 THREAD INTEGRITY:")
        print(f"  Unique threads:     {len(thread_counts)}")
        print(f"  Avg turns/thread:   {len(filtered_turns)/max(len(thread_counts),1):.1f}")
        print(f"  Max thread length:  {max(thread_counts.values()) if thread_counts else 0}")

        # Top contributing files
        file_counts = {}
        for turn in filtered_turns:
            file_counts[turn.source_file] = file_counts.get(turn.source_file, 0) + 1
        print(f"\n📊 TOP CONTRIBUTING FILES:")
        for fname, count in sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:15]:
            print(f"  {fname:<55} {count:>4} turns")


if __name__ == "__main__":
    parser = CouncilCorpusParser(
        input_dir="../../NeuroCognica_Primus/convos",
        output_file="training_data/council_turns.jsonl"
    )
    parser.parse_files()
