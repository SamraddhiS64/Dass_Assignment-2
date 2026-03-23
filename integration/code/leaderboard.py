import data

def get_leaderboard():
    tally = {}
    for r in data.results:
        w = r["winner"]
        if w not in tally:
            tally[w] = {"wins": 0, "earnings": 0, "races": 0}
        tally[w]["wins"] += 1
        tally[w]["earnings"] += r["prize"]
    for name in data.crew_members:
        if name not in tally:
            tally[name] = {"wins": 0, "earnings": 0}
    return sorted(tally.items(), key=lambda x: (-x[1]["wins"], -x[1]["earnings"]))

def print_leaderboard():
    board = get_leaderboard()
    print("  === All-Time Leaderboard ===")
    for rank, (name, stats) in enumerate(board, 1):
        print(f"  #{rank} {name} | Wins: {stats['wins']} | Earnings: ${stats['earnings']}")