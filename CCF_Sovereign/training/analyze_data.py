"""Quick analysis of extracted training data."""
import json

with open('training_data/council_turns.jsonl', encoding='utf-8') as f:
    turns = [json.loads(line) for line in f if line.strip()]

print(f"Total turns: {len(turns)}")

# Response length stats
lengths = [len(t['response']) for t in turns]
lengths.sort(reverse=True)
print(f"Top 10 response lengths: {lengths[:10]}")
print(f"Average response length: {sum(lengths)/len(lengths):.0f} chars")
print(f"Median response length: {lengths[len(lengths)//2]:.0f} chars")

# Check sparks file turns
sparks = [t for t in turns if 'sparks' in t['source_file']]
print(f"\nSparks file turns: {len(sparks)}")
for t in sparks:
    print(f"  prompt ({len(t['prompt'])} chars): {t['prompt'][:80]}...")
    print(f"  response: {len(t['response'])} chars")

# Check geminiupdate
gem = [t for t in turns if 'geminiupdate' in t['source_file']]
print(f"\nGeminiupdate1 turns: {len(gem)}")
for t in gem:
    print(f"  prompt ({len(t['prompt'])} chars): {t['prompt'][:80]}...")
    print(f"  response: {len(t['response'])} chars, format: {t['file_format']}")

# Persona stats
print(f"\nPersona breakdown:")
personas = {}
for t in turns:
    personas[t['persona']] = personas.get(t['persona'], 0) + 1
for persona, count in sorted(personas.items()):
    print(f"  {persona}: {count}")

# Response length distribution
print(f"\nResponse length distribution:")
buckets = [0, 100, 500, 1000, 2000, 5000, 10000, 16001]
for i in range(len(buckets)-1):
    count = sum(1 for l in lengths if buckets[i] <= l < buckets[i+1])
    print(f"  {buckets[i]:>5}-{buckets[i+1]:>5} chars: {count:>4} turns")
