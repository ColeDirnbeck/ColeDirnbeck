#include <iostream>
#include <string>
#include <cstdlib>
#include <ctime>
using namespace std;

class Dice
{
private:
    int sides;
    int roll;
public:
    Dice(void);
    Dice(int);
    int rollDice(void);
};

Dice::Dice(void)
{
    sides = 6;
    roll = 0;
    srand(time(NULL));
}
Dice::Dice(int s)
{
    sides = s;
    roll = 0;
    srand(time(NULL));
}
int Dice::rollDice(void)
{
    roll = (rand() % sides + 1);
    return roll;
}

class Player
{
private:
    string playerName;
    int bank;
public:
    Player(void);
    Player(string);
    void bankScore(int);
    int getBank(void);
    string getName(void);
};

Player::Player(void)
{
    playerName = "Player 1";
    bank = 0;
}

Player::Player(string S)
{
    playerName = S;
    bank = 0;
}

void Player::bankScore(int addIt)
{
    bank = bank + addIt;
}

int Player::getBank(void)
{
    return bank;
}

string Player::getName(void)
{
    return playerName;
}

class PlayerTwo
{
private:
    string playerNameTwo;
    int bankTwo;
public:
    PlayerTwo(void);
    PlayerTwo(string);
    void bankScoreTwo(int);
    int getBankTwo(void);
    string getNameTwo(void);
};

PlayerTwo::PlayerTwo(void)
{
    playerNameTwo = "Player 2";
    bankTwo = 0;
}

PlayerTwo::PlayerTwo(string S)
{
    playerNameTwo = S;
    bankTwo = 0;
}

void PlayerTwo::bankScoreTwo(int addItTwo)
{
    bankTwo = bankTwo + addItTwo;
}

int PlayerTwo::getBankTwo(void)
{
    return bankTwo;
}

string PlayerTwo::getNameTwo(void)
{
    return playerNameTwo;
}

int main()
{

    int goal = 100; // could even add a user input to change the goal limit, but the prompt asks for 100. 
    int rollValue = 0;
    int roundTotal, roundTotalTwo = 0;
    bool playerTurn = 0;
    char choice;
    string playerName;
    string playerNameTwo;
    Dice myDiceRoll;

    cout << "Welcome to the game of Pig!" << endl;
    cout << "Each turn, a player can continuously roll a dice until either a 1 is rolled or they choose to hold their score." << endl;
    cout << "Rolling a 1 will 0 the player's round score and will end their turn." << endl;
    cout << "The objective: first player to 100 wins!" << endl;

    cout << "\nPlayer 1, what is your name?" << endl;

    cin >> playerName;
    Player myPlayer(playerName);

    cout << "Player 2, what is your name?" << endl;
    cin >> playerNameTwo;
    PlayerTwo myPlayerTwo(playerNameTwo);

    rollValue = myDiceRoll.rollDice();

    do
    {
        roundTotal = 0;

        do
        {
            rollValue = myDiceRoll.rollDice();
            cout << "\nPlayer " << myPlayer.getName() << " rolled a " << rollValue << endl;

            if (rollValue > 1)
            {
                roundTotal = roundTotal + rollValue;
                cout << "Player " << myPlayer.getName() << "'s current round total is: " << roundTotal << endl;
                cout << "Player " << myPlayer.getName() << "'s banked total is: " << myPlayer.getBank() << endl;
                cout << "Do you want to roll again? Y/y or N/n " << endl;
                cin >> choice;

                if (choice == 'Y' || choice == 'y')
                {
                    cout << "You selected to roll again." << endl;
                    playerTurn = 1;
                }
                else if (choice == 'N' || choice == 'n')
                {
                    cout << "You selected to end your turn.\n" << endl;
                    playerTurn = 0;
                    myPlayer.bankScore(roundTotal);
                    roundTotal = 0;
                }
                else
                {
                    cout << "\nNot a valid response..." << endl;
                    cout << "Do you want to roll again? Y/y or N/n " << endl;
                    cin >> choice;

                    if (choice != 'N' && choice != 'n' && choice != 'Y' && choice != 'y')
                    {
                        do
                        {
                            cout << "\nNot a valid response..." << endl;
                            cout << "Do you want to roll again? Y/y or N/n " << endl;
                            cin >> choice;
                        } while (choice != 'N' && choice != 'n' && choice != 'Y' && choice != 'y');
                    }
                }
            }
            else
            {
                cout << "\nPlayer " << myPlayer.getName() << " rolled a 1 and lost their turn." << endl;
                roundTotal = 0;
                playerTurn = 0;
            }
        } while (playerTurn == 1 && myPlayer.getBank() < goal && myPlayer.getBank() != goal);

        if (myPlayer.getBank() > goal)
        {
            cout << "Player " << myPlayer.getName() << " has won!" << endl;
            break;
        }

        roundTotalTwo = 0;

        do
        {
            rollValue = myDiceRoll.rollDice();
            cout << "\nPlayer " << myPlayerTwo.getNameTwo() << " rolled a " << rollValue << endl;

            if (rollValue > 1)
            {
                roundTotalTwo = roundTotalTwo + rollValue;
                cout << "Player " << myPlayerTwo.getNameTwo() << "'s current round total is: " << roundTotalTwo << endl;
                cout << "Player " << myPlayerTwo.getNameTwo() << "'s banked total is: " << myPlayerTwo.getBankTwo() << endl;
                cout << "Do you want to roll again? Y/y or N/n " << endl;
                cin >> choice;

                if (choice == 'Y' || choice == 'y')
                {
                    cout << "You selected to roll again." << endl;
                    playerTurn = 0;
                }
                else if (choice == 'N' || choice == 'n')
                {
                    cout << "You selected to end your turn.\n" << endl;
                    playerTurn = 1;
                    myPlayerTwo.bankScoreTwo(roundTotalTwo);
                    roundTotalTwo = 0;
                }
                else
                {
                    cout << "\nNot a valid response..." << endl;
                    cout << "Do you want to roll again? Y/y or N/n " << endl;
                    cin >> choice;

                    if (choice != 'N' && choice != 'n' && choice != 'Y' && choice != 'y')
                        do
                        {
                            cout << "\nNot a valid response..." << endl;
                            cout << "Do you want to roll again? Y/y or N/n " << endl;
                            cin >> choice;
                        } while (choice != 'N' && choice != 'n' && choice != 'Y' && choice != 'y');
                }
            }
            else
            {
                cout << "\nPlayer " << playerNameTwo << " rolled a 1 and lost their turn." << endl;
                roundTotalTwo = 0;
                playerTurn = 1;
            }
        } while (playerTurn == 0 && myPlayerTwo.getBankTwo() < goal && myPlayerTwo.getBankTwo() != goal);

        if (myPlayerTwo.getBankTwo() > goal)
        {
            cout << "Player " << myPlayerTwo.getNameTwo() << " has won!" << endl;
            break;
        }

    } while (myPlayer.getBank() != goal && myPlayerTwo.getBankTwo() != goal && myPlayer.getBank() < goal && myPlayerTwo.getBankTwo() < goal);

    return 0;
}