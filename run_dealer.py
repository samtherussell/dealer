from dealer.main import run_game_for_n_players


def main():

    while True:
        num_players = int(input("# players: "))
        if num_players > 1:
            break
        print("must have more than one player")

    run_game_for_n_players(num_players)


if __name__ == "__main__":
    main()
