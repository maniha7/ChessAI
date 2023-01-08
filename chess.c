#include <string.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include <time.h>
#include <windows.h>
#include <float.h>

//orientations:
//white:0
//black:1

//White
//1 - Pawn
//2 - Rook
//3 - Knight
//4 - Bishop
//5 - Queen
//6 - King
//Black
//11 - Pawn
//12 - Rook
//13 - Knight
//14 - Bishop
//15 - Queen
//16 - King

//move is int of form x*10+y, resulting in xy 2 digit integer representing tile to move to
typedef struct Moveset
{
    int *array;
    size_t used; //moves in moveset
    size_t size; //moveset size
} Moveset;

typedef struct Watchlist
{
    int array[35];
    size_t used;
    size_t size;
} Watchlist;

typedef struct Piece
{
    int x;
    int y;
    int type;
    int ind; //index in gamestate pieceList
    bool alive;
    int numMoves;
    struct Moveset *moveset;
    struct Watchlist *watchlist;
} Piece;

typedef struct Gamestate
{
    int board[8][8];        //-1 if empty, else index in pieceList of respective piece on this tile
    int watchMap[8][8][32]; //for each tile, bitmap of piece indexes watching that tile
    int wAtt[8][8];         //white attacker count per tile
    int bAtt[8][8];         //black attacker count per tile
    Piece *pieceList[32];   //populate with every piece struct in game, counted left-right, bottom-top from chess board, white on bottom
    int numAlive;
    bool zeroPlayer;
} Gamestate;

//*******************************************************************************************************************************************************************

//init a watchlist
Watchlist *initWatchlist()
{
    Watchlist *w = malloc(sizeof(Watchlist));
    if (w == NULL)
    {
        return NULL;
    }
    w->used = 0;
    w->size = 35;
    return w;
}

//init a moveset of size sz
Moveset *initMoveset()
{

    Moveset *m = malloc(sizeof(Moveset));
    //return null if no memory left
    if (m == NULL)
    {
        return NULL;
    }
    //moveset list
    m->array = malloc(35 * sizeof(int));

    //return null and free moveset struct if no memory
    if (m->array == NULL)
    {
        free(m);
        return NULL;
    }
    m->used = 0;
    m->size = 35;
    return m;
}

void clearMoveset(Moveset *m)
{
    if (m != NULL)
    {
        m->used = 0;
    }
}

void deleteMoveset(Moveset *m)
{
    if (m != NULL)
    {
        free(m->array);
        free(m);
    }
}

//input from init gamestate with [x, y, alive, nummoves, type, pieceIndex]
Piece *initPiece(int arr[6])
{

    //change size?
    int sz = 35;

    int x = arr[0];
    int y = arr[1];
    bool alive = arr[2] == 0 ? false : true;
    int nummoves = arr[3];
    int type = arr[4];
    int ind = arr[5];

    Piece *piece = malloc(sizeof(Piece));
    if (piece == NULL)
    {
        return NULL;
    }
    piece->x = x;
    piece->y = y;
    piece->type = type;
    piece->ind = ind;
    piece->alive = alive;
    piece->numMoves = nummoves;
    piece->moveset = initMoveset();
    //if moveset not loaded correctly free piece
    if (piece->moveset == NULL)
    {
        free(piece);
        return NULL;
    }
    piece->watchlist = initWatchlist();
    if (piece->watchlist == NULL)
    {
        free(piece->moveset->array);
        free(piece->moveset);
        free(piece);
        return NULL;
    }

    return piece;
}

void freePiece(Piece *piece)
{
    //delete moveset
    deleteMoveset(piece->moveset);

    //delete watchlist
    free(piece->watchlist);

    //delete self
    free(piece);
}

//add watcher to gamestate watch map when a piece is attacking a tile
void addWatch(int x, int y, Piece *piece, Gamestate *game)
{

    //update piece watchlist
    if (piece->watchlist->used != piece->watchlist->size)
    {

        int orientation = 0;
        if (piece->type > 10)
        {
            orientation = 1;
        }

        //ignore special pawn case which cant attack/"watch" forward moves
        if (!(piece->type == 1 || piece->type == 11) || x != piece->x)
        {
            piece->watchlist->array[piece->watchlist->used] = x * 10 + y;
            piece->watchlist->used += 1;
            //update game watchmap
            game->watchMap[y][x][piece->ind] = 1;

            if (orientation == 0)
            {
                game->wAtt[y][x] += 1;
            }
            else
            {
                game->bAtt[y][x] += 1;
            }
        }
    }
    else
    {
        printf("%d\n", 888888);
    }
}

//remove tiles that a piece is watching after it has moved away
void removeWatch(Piece *piece, Gamestate *game)
{
    if (piece->alive && piece->watchlist->used > 0)
    {
        int orientation = 0;
        if (piece->type > 10)
        {
            orientation = 1;
        }
        int ind = piece->ind;
        for (int i = 0; i < piece->watchlist->used; i++)
        {
            int watch = piece->watchlist->array[i];
            int wy = watch % 10;
            int wx = (watch - wy) / 10;
            game->watchMap[wy][wx][ind] = 0;
            if (orientation == 0)
            {
                game->wAtt[wy][wx] -= 1;
            }
            else
            {
                game->bAtt[wy][wx] -= 1;
            }
        }
        piece->watchlist->used = 0;
    }
}

void addMove(Piece *piece, Gamestate *game, int move)
{

    //shouldn't run out of space unless piece accumulates to many moves by some error
    if (piece->moveset->used != piece->moveset->size)
    {

        int tmove = move;
        if (tmove >= 900)
        {
            tmove -= 900;
        }
        int y = tmove % 10;
        int x = (tmove - y) / 10;

        addWatch(x, y, piece, game);
        piece->moveset->array[piece->moveset->used] = move;
        piece->moveset->used += 1;
    }
    else
    {
        printf("%d\n", 888888);
    }
}

bool isAttacked(int x, int y, int orientation, Gamestate *game)
{
    if (orientation == 0)
    {
        if (game->bAtt[y][x] == 0)
        {
            return false;
        }
    }
    else
    {
        if (game->wAtt[y][x] == 0)
        {
            return false;
        }
    }

    return true;
}

bool isEnemy(int orientation, int pieceType)
{
    if (orientation == 0)
    {
        if (pieceType > 10 && pieceType != 16)
        {
            return true;
        }
    }
    else if (pieceType < 10 && pieceType != 6)
    {
        return true;
    }
    return false;
}

void getKingMove(int x, int y, Piece *piece, int orientation, Gamestate *game)
{
    for (int cy = -1; cy < 2; cy++)
    {
        if (y + cy < 0 || y + cy > 7)
        {
            continue;
        }
        for (int cx = -1; cx < 2; cx++)
        {
            if (x + cx < 0 || x + cx > 7 || (cx == 0 && cy == 0))
            {
                continue;
            }

            if (game->board[y + cy][x + cx] == -1 && !isAttacked(x + cx, y + cy, orientation, game))
            {
                addMove(piece, game, (x + cx) * 10 + y + cy);
            }
            else
            {
                if (game->board[y + cy][x + cx] != -1 && isEnemy(orientation, game->pieceList[game->board[y + cy][x + cx]]->type) && !isAttacked(x + cx, y + cy, orientation, game))
                {
                    addMove(piece, game, (x + cx) * 10 + y + cy);
                }
                else
                {
                    addWatch(x + cx, y + cy, piece, game);
                }
            }
        }
    }
}

void getRookMove(int x, int y, Piece *piece, int orientation, Gamestate *game)
{
    bool U = true;
    bool R = true;
    bool D = true;
    bool L = true;
    int change = 0;
    while (U || R || D || L)
    {
        change += 1;
        //check edges
        if (y - change < 0)
        {
            U = false;
        }
        if (x + change > 7)
        {
            R = false;
        }
        if (y + change > 7)
        {
            D = false;
        }
        if (x - change < 0)
        {
            L = false;
        }

        //check blocks / add moves
        if (U)
        {
            if (game->board[y - change][x] == -1)
            {
                addMove(piece, game, x * 10 + y - change);
            }
            else
            {
                U = false;
                if (isEnemy(orientation, game->pieceList[game->board[y - change][x]]->type))
                {
                    addMove(piece, game, x * 10 + y - change);
                }
                else
                {
                    addWatch(x, y - change, piece, game);
                }
            }
        }
        if (R)
        {
            if (game->board[y][x + change] == -1)
            {
                addMove(piece, game, (x + change) * 10 + y);
            }
            else
            {
                R = false;
                if (isEnemy(orientation, game->pieceList[game->board[y][x + change]]->type))
                {
                    addMove(piece, game, (x + change) * 10 + y);
                }
                else
                {
                    addWatch(x + change, y, piece, game);
                }
            }
        }
        if (D)
        {
            if (game->board[y + change][x] == -1)
            {
                addMove(piece, game, x * 10 + y + change);
            }
            else
            {
                D = false;
                if (isEnemy(orientation, game->pieceList[game->board[y + change][x]]->type))
                {
                    addMove(piece, game, x * 10 + y + change);
                }
                else
                {
                    addWatch(x, y + change, piece, game);
                }
            }
        }
        if (L)
        {
            if (game->board[y][x - change] == -1)
            {
                addMove(piece, game, (x - change) * 10 + y);
            }
            else
            {
                L = false;
                if (isEnemy(orientation, game->pieceList[game->board[y][x - change]]->type))
                {
                    addMove(piece, game, (x - change) * 10 + y);
                }
                else
                {
                    addWatch(x - change, y, piece, game);
                }
            }
        }
    }
}

void getBishopMove(int x, int y, Piece *piece, int orientation, Gamestate *game)
{
    bool UL = true;
    bool UR = true;
    bool DL = true;
    bool DR = true;
    int change = 0;
    while (UL || UR || DL || DR)
    {
        change += 1;
        //check edges
        if (y - change < 0)
        {
            UL = false;
            UR = false;
        }
        if (y + change > 7)
        {
            DL = false;
            DR = false;
        }
        if (x - change < 0)
        {
            UL = false;
            DL = false;
        }
        if (x + change > 7)
        {
            UR = false;
            DR = false;
        }

        //check blocks / add moves
        if (UL)
        {
            if (game->board[y - change][x - change] == -1)
            {
                addMove(piece, game, (x - change) * 10 + y - change);
            }
            else
            {
                UL = false;
                if (isEnemy(orientation, game->pieceList[game->board[y - change][x - change]]->type))
                {
                    addMove(piece, game, (x - change) * 10 + y - change);
                }
                else
                {
                    addWatch(x - change, y - change, piece, game);
                }
            }
        }
        if (UR)
        {
            if (game->board[y - change][x + change] == -1)
            {
                addMove(piece, game, (x + change) * 10 + y - change);
            }
            else
            {
                UR = false;
                if (isEnemy(orientation, game->pieceList[game->board[y - change][x + change]]->type))
                {
                    addMove(piece, game, (x + change) * 10 + y - change);
                }
                else
                {
                    addWatch(x + change, y - change, piece, game);
                }
            }
        }
        if (DL)
        {
            if (game->board[y + change][x - change] == -1)
            {
                addMove(piece, game, (x - change) * 10 + y + change);
            }
            else
            {
                DL = false;
                if (isEnemy(orientation, game->pieceList[game->board[y + change][x - change]]->type))
                {
                    addMove(piece, game, (x - change) * 10 + y + change);
                }
                else
                {
                    addWatch(x - change, y + change, piece, game);
                }
            }
        }
        if (DR)
        {
            if (game->board[y + change][x + change] == -1)
            {
                addMove(piece, game, (x + change) * 10 + y + change);
            }
            else
            {
                DR = false;
                if (isEnemy(orientation, game->pieceList[game->board[y + change][x + change]]->type))
                {
                    addMove(piece, game, (x + change) * 10 + y + change);
                }
                else
                {
                    addWatch(x + change, y + change, piece, game);
                }
            }
        }
    }
}

void getKnightMove(int x, int y, Piece *piece, int orientation, Gamestate *game)
{
    //up sides
    if (y > 0)
    {
        if (x > 1)
        {
            if (game->board[y - 1][x - 2] == -1 || isEnemy(orientation, game->pieceList[game->board[y - 1][x - 2]]->type))
            {
                addMove(piece, game, (x - 2) * 10 + y - 1);
            }
            else
            {
                addWatch(x - 2, y - 1, piece, game);
            }
        }
        if (x < 6)
        {
            if (game->board[y - 1][x + 2] == -1 || isEnemy(orientation, game->pieceList[game->board[y - 1][x + 2]]->type))
            {
                addMove(piece, game, (x + 2) * 10 + y - 1);
            }
            else
            {
                addWatch(x + 2, y - 1, piece, game);
            }
        }
    }
    //ups
    if (y > 1)
    {
        if (x > 0)
        {
            if (game->board[y - 2][x - 1] == -1 || isEnemy(orientation, game->pieceList[game->board[y - 2][x - 1]]->type))
            {
                addMove(piece, game, (x - 1) * 10 + y - 2);
            }
            else
            {
                addWatch(x - 1, y - 2, piece, game);
            }
        }
        if (x < 7)
        {
            if (game->board[y - 2][x + 1] == -1 || isEnemy(orientation, game->pieceList[game->board[y - 2][x + 1]]->type))
            {
                addMove(piece, game, (x + 1) * 10 + y - 2);
            }
            else
            {
                addWatch(x + 1, y - 2, piece, game);
            }
        }
    }
    //down sides
    if (y < 7)
    {
        if (x > 1)
        {
            if (game->board[y + 1][x - 2] == -1 || isEnemy(orientation, game->pieceList[game->board[y + 1][x - 2]]->type))
            {
                addMove(piece, game, (x - 2) * 10 + y + 1);
            }
            else
            {
                addWatch(x - 2, y + 1, piece, game);
            }
        }
        if (x < 6)
        {
            if (game->board[y + 1][x + 2] == -1 || isEnemy(orientation, game->pieceList[game->board[y + 1][x + 2]]->type))
            {
                addMove(piece, game, (x + 2) * 10 + y + 1);
            }
            else
            {
                addWatch(x + 2, y + 1, piece, game);
            }
        }
    }
    //downs
    if (y < 6)
    {
        if (x > 0)
        {
            if (game->board[y + 2][x - 1] == -1 || isEnemy(orientation, game->pieceList[game->board[y + 2][x - 1]]->type))
            {
                addMove(piece, game, (x - 1) * 10 + y + 2);
            }
            else
            {
                addWatch(x - 1, y + 2, piece, game);
            }
        }
        if (x < 7)
        {
            if (game->board[y + 2][x + 1] == -1 || isEnemy(orientation, game->pieceList[game->board[y + 2][x + 1]]->type))
            {
                addMove(piece, game, (x + 1) * 10 + y + 2);
            }
            else
            {
                addWatch(x + 1, y + 2, piece, game);
            }
        }
    }
}

void getQueenMove(int x, int y, Piece *piece, int orientation, Gamestate *game)
{
    getRookMove(x, y, piece, orientation, game);
    getBishopMove(x, y, piece, orientation, game);
}

void getPawnMove(int x, int y, Piece *piece, int orientation, Gamestate *game)
{
    static int counter = 0;
    counter++;

    if (orientation == 1)
    {
        //forward
        if (game->board[y + 1][x] == -1)
        {
            if (y + 1 < 7)
            {

                addMove(piece, game, x * 10 + y + 1);

                //check for first move double forward
                if (piece->numMoves == 0 && game->board[y + 2][x] == -1)
                {
                    addMove(piece, game, x * 10 + y + 2);
                }
            }
            else
            {
                //promotion
                addMove(piece, game, 900 + (x * 10) + y + 1);
            }
        }

        //attack left
        if (x - 1 > -1)
        {
            if (game->board[y + 1][x - 1] != -1 && isEnemy(orientation, game->pieceList[game->board[y + 1][x - 1]]->type))
            {
                if (y + 1 < 7)
                {
                    addMove(piece, game, (x - 1) * 10 + y + 1);
                }
                else
                {
                    addMove(piece, game, 900 + ((x - 1) * 10) + y + 1);
                }
            }
            else
            {
                addWatch(x - 1, y + 1, piece, game);
            }
        }
        //attack right
        if (x + 1 < 8)
        {
            if (game->board[y + 1][x + 1] != -1 && isEnemy(orientation, game->pieceList[game->board[y + 1][x + 1]]->type))
            {
                if (y + 1 < 7)
                {
                    addMove(piece, game, (x + 1) * 10 + y + 1);
                }
                else
                {
                    addMove(piece, game, 900 + ((x + 1) * 10) + y + 1);
                }
            }
            else
            {
                addWatch(x + 1, y + 1, piece, game);
            }
        }
    }
    else
    {

        //forward
        if (game->board[y - 1][x] == -1)
        {
            if (y - 1 > 0)
            {
                addMove(piece, game, x * 10 + y - 1);
                if (piece->numMoves == 0 && game->board[y - 2][x] == -1)
                {

                    addMove(piece, game, x * 10 + y - 2);
                }
            }
            else
            {
                //promotion
                addMove(piece, game, 900 + (x * 10) + y - 1);
            }
        }
        //attack left
        if (x - 1 > -1)
        {
            if (game->board[y - 1][x - 1] != -1 && isEnemy(orientation, game->pieceList[game->board[y - 1][x - 1]]->type))
            {
                if (y - 1 > 0)
                {
                    addMove(piece, game, (x - 1) * 10 + y - 1);
                }
                else
                {
                    addMove(piece, game, 900 + ((x - 1) * 10) + y - 1);
                }
            }
            else
            {
                addWatch(x - 1, y - 1, piece, game);
            }
        }

        //attack right
        if (x + 1 < 8)
        {
            if (game->board[y - 1][x + 1] != -1 && isEnemy(orientation, game->pieceList[game->board[y - 1][x + 1]]->type))
            {
                if (y - 1 > 0)
                {
                    addMove(piece, game, (x + 1) * 10 + y - 1);
                }
                else
                {
                    addMove(piece, game, 900 + ((x + 1) * 10) + y - 1);
                }
            }
            else
            {
                addWatch(x + 1, y - 1, piece, game);
            }
        }
    }
}

void getMove(Piece *piece, Gamestate *game)
{
    if (piece->alive)
    {
        int x = piece->x;
        int y = piece->y;

        int orientation;
        if (piece->type > 10)
        {
            orientation = 1;
        }
        else
        {
            orientation = 0;
        }

        //free space of old moves?
        removeWatch(piece, game);
        clearMoveset(piece->moveset);

        //pawn move
        if (piece->type == 1 || piece->type == 11)
        {
            getPawnMove(x, y, piece, orientation, game);
        }
        //rook move
        if (piece->type == 2 || piece->type == 12)
        {
            getRookMove(x, y, piece, orientation, game);
        }
        //knight move
        if (piece->type == 3 || piece->type == 13)
        {
            getKnightMove(x, y, piece, orientation, game);
        }
        //bishop move
        if (piece->type == 4 || piece->type == 14)
        {
            getBishopMove(x, y, piece, orientation, game);
        }
        //queen move
        if (piece->type == 5 || piece->type == 15)
        {
            getQueenMove(x, y, piece, orientation, game);
        }
        //king move
        if (piece->type == 6 || piece->type == 16)
        {
            getKingMove(x, y, piece, orientation, game);
        }
    }
}

double *getScore(int cOrientation, Gamestate *game, int depth, Piece *recentPiece, int turns)
{
    double score;
    double eScore;
    int orientation;
    double *r = malloc(2 * sizeof(double));

    //if not 0 player, we only care about the AI's score, playing black
    if (game->zeroPlayer)
    {
        orientation = 1 - (turns % 2);
    }
    else
    {
        orientation = 1;
    }

    //orientation dependent vars
    int indOffset = 0;
    int kingInd = 4;
    int check = 0;
    if (orientation == 1)
    {
        kingInd = 28;
        indOffset = 16;
    }

    //are you in check as result of move (illegal -- give worst score)
    int kingX = game->pieceList[kingInd]->x;
    int kingY = game->pieceList[kingInd]->y;
    if (orientation == 0)
    {
        if (game->bAtt[kingY][kingX] > 0)
        {
            score = -88888.88888;
            eScore = 30.0; //lol?
            r[0] = score;
            r[1] = eScore;
            return r;
        }
    }
    else
    {
        if (game->wAtt[kingY][kingX] > 0)
        {
            score = -88888.88888;
            eScore = 30.0;
            r[0] = score;
            r[1] = eScore;
            return r;
        }
    }

    //checkmate checks
    if (orientation == cOrientation)
    {
        Piece *eKing;
        if (orientation == 1)
        {
            eKing = game->pieceList[4];
            if (eKing->moveset->used == 0 && game->bAtt[eKing->y][eKing->x] > 0 && game->wAtt[recentPiece->y][recentPiece->x] == 0)
            {
                score = 777.777;
                eScore = 77.7;
                r[0] = score;
                r[1] = eScore;
                return r;
            }
        }
        else
        {
            eKing = game->pieceList[28];
            if (eKing->moveset->used == 0 && game->wAtt[eKing->y][eKing->x] > 0 && game->bAtt[recentPiece->y][recentPiece->x] == 0)
            {
                score = 777.777;
                eScore = 77.7;
                r[0] = score;
                r[1] = eScore;
                return r;
            }
        }
    }
    else
    {
        Piece *yKing;
        if (orientation == 1)
        {
            yKing = game->pieceList[28];
            if (yKing->moveset->used == 0 && game->wAtt[yKing->y][yKing->x] > 0 && game->bAtt[recentPiece->y][recentPiece->x] == 0)
            {
                score = -777.777;
                eScore = -77.7;
                r[0] = score;
                r[1] = eScore;
                return r;
            }
        }
        else
        {
            yKing = game->pieceList[4];
            if (yKing->moveset->used == 0 && game->bAtt[yKing->y][yKing->x] > 0 && game->wAtt[recentPiece->y][recentPiece->x] == 0)
            {
                score = -777.777;
                eScore = -77.7;
                r[0] = score;
                r[1] = eScore;
                return r;
            }
        }
    }

    //queen attacked or lost
    int queenPenalty = 0;
    int eQueenPenalty = 0;

    //num tiles watched by player (duplicates counted)
    int yWatches = 0;
    int eWatches = 0;

    //num moves available to player
    int yMoves = 0;
    int eMoves = 0;

    //weighted piece scores of players
    int yPScore = 0;
    int ePScore = 0;

    //(# of times own piece is attacked)*piece weight, for all pieces of each player
    int yRiskScore = 0;
    int eRiskScore = 0;

    int pieceWeights[6] = {1, 5, 3, 3, 9, 9};
    for (int i = 0; i < 32; i++)
    {

        Piece *piece = game->pieceList[i];

        //queen penalties
        if (i == 27)
        {
            if (orientation == 1)
            {
                if (!piece->alive || game->wAtt[piece->y][piece->x] > 0)
                {
                    queenPenalty = 12;
                }
            }
            else if (!piece->alive)
            {
                eQueenPenalty = 12;
            }
        }
        if (i == 3)
        {
            if (orientation == 0)
            {
                if (!piece->alive || game->bAtt[piece->y][piece->x] > 0)
                {
                    queenPenalty = 12;
                }
            }
            else if (!piece->alive)
            {
                eQueenPenalty = 9;
            }
        }

        //general piece scores
        if (piece->alive)
        {
            if (orientation == 1)
            {
                if (i > 15)
                {
                    yRiskScore += game->wAtt[piece->y][piece->x] * pieceWeights[piece->type - 11];
                    yPScore += pieceWeights[piece->type - 11];
                    yMoves += piece->moveset->used;
                    yWatches += piece->watchlist->used;
                }
                else
                {
                    eRiskScore += game->bAtt[piece->y][piece->x] * pieceWeights[piece->type - 1];
                    ePScore += pieceWeights[piece->type - 1];
                    eMoves += piece->moveset->used;
                    eWatches += piece->watchlist->used;
                }
            }
            else
            {
                if (i <= 15)
                {
                    yRiskScore += game->bAtt[piece->y][piece->x] * pieceWeights[piece->type - 1];
                    yPScore += pieceWeights[piece->type - 1];
                    yMoves += piece->moveset->used;
                    yWatches += piece->watchlist->used;
                }
                else
                {
                    eRiskScore += game->wAtt[piece->y][piece->x] * pieceWeights[piece->type - 11];
                    ePScore += pieceWeights[piece->type - 11];
                    eMoves += piece->moveset->used;
                    eWatches += piece->watchlist->used;
                }
            }
        }
    }
    int watchDif = yWatches - eWatches;
    int moveDif = yMoves - eMoves;
    int scoreDif = yPScore - ePScore;
    int ewatchDif = eWatches - yWatches;
    int emoveDif = eMoves - yMoves;
    int escoreDif = ePScore - yPScore;
    double dWatch = (double)watchDif;
    double dMove = (double)moveDif;
    double dScore = (double)scoreDif;
    double edWatch = (double)ewatchDif;
    double edMove = (double)emoveDif;
    double edScore = (double)escoreDif;

    if (depth > 0)
    {
        //set limits
        if (watchDif > 15)
        {
            dWatch = 15.0;
        }
        if (watchDif < -15)
        {
            dWatch = -15.0;
        }
        if (moveDif > 15)
        {
            dMove = 15.0;
        }
        if (moveDif < -15)
        {
            dMove = -15.0;
        }
    }
    //make piece dif a bit more important near the end to encourage queening and such
    int dScale = 1;
    if (turns > 20)
    {
        dScale = 3;
    }

    eScore = (edScore * dScale) + ((double)yRiskScore) / 2.0 - ((double)eRiskScore) / 2.0 - (double)eQueenPenalty + (double)queenPenalty + edMove + edWatch;
    score = (dScore * dScale) - ((double)yRiskScore) / 2.0 + ((double)eRiskScore) / 2.0 - (double)queenPenalty + (double)eQueenPenalty + dMove + dWatch;

    //printf("**SCORE: %f\n", score);

    //printf("score: %d\n", score);
    //printf("best: %d\n", best);
    //pawn penalty

    int pawnPenalty = -2.0;
    if (game->numAlive <= 18)
    {
        Piece *eKing;

        if (orientation == 1)
        {
            eKing = game->pieceList[4];
        }
        else
        {
            eKing = game->pieceList[28];
        }
        //king movability
        score -= eKing->moveset->used * 2;
        pawnPenalty = 2.0;
        if (game->numAlive <= 11)
        {
            score -= eKing->moveset->used * 3;
            pawnPenalty = 4.0;
        }
    }
    //pawn movement penalties
    if (recentPiece->type == 1)
    {
        if (recentPiece->y == 0 && game->bAtt[recentPiece->y][recentPiece->x] == 0)
        {
            if (orientation == 1)
            {
                score = score + 60.0;
            }
            else
            {
                score = score - 60.0;
            }
        }
        else if (orientation == 0)
        {
            score = score + pawnPenalty;
        }
    }
    if (recentPiece->type == 11)
    {
        if (recentPiece->y == 7 && game->wAtt[recentPiece->y][recentPiece->x] == 0)
        {
            if (orientation == 1)
            {
                score = score + 60.0;
            }
            else
            {
                score = score - 60.0;
            }
        }
        else if (orientation == 1)
        {
            score = score + pawnPenalty;
        }
    }
    r[0] = score;
    r[1] = eScore;
    return r;
}

//returns [oldLocation, captured-pieceIndex, score]
long *testMove(int move, int orientation, Piece *piece, Gamestate *game, int turns, int depth)
{
    long takenVal = -1;
    int pieceWeights[6] = {1, 5, 3, 3, 9, 2};

    //increment num moves
    piece->numMoves += 1;

    //save old x,y in temp
    //if move is pawn promotion, promote pawn and give oldLocation return value >900 so we know to undo it later
    long oldLoc = piece->x * 10 + piece->y;
    int oldX = piece->x;
    int oldY = piece->y;
    if (move >= 900)
    {
        if (orientation == 0)
        {
            piece->type = 5;
        }
        else
        {
            piece->type = 15;
        }
        move -= 900;
        oldLoc += 900;
    }

    int newY = move % 10;
    int newX = (move - newY) / 10;

    //if an enemy piece is on this tile, copy its pieceIndex (save in temp) and remove it from the gamestate board[][] (also make it not alive) ***PRIORITIZE IF FREE PIECE***
    long taken = -1;
    if (game->board[newY][newX] != -1)
    {
        game->numAlive -= 1;
        taken = game->board[newY][newX];
        Piece *tPiece = game->pieceList[taken];
        removeWatch(tPiece, game);
        tPiece->alive = false;
        if (orientation == 1)
        {
            takenVal = pieceWeights[tPiece->type - 1];
        }
        else
        {
            takenVal = pieceWeights[tPiece->type - 11];
        }
    }

    //move piece
    game->board[newY][newX] = piece->ind;
    game->board[oldY][oldX] = -1;
    piece->x = newX;
    piece->y = newY;

    //recall getMove() for moving piece and all pieces listed as watching the tile moved to and tile moved away from
    getMove(piece, game);

    for (int i = 0; i < 32; i++)
    {
        if (i != 4 && i != 28 && i != piece->ind && game->pieceList[i]->alive && (game->watchMap[newY][newX][i] != 0 || game->watchMap[oldY][oldX][i] != 0 || game->pieceList[i]->type == 1 || game->pieceList[i]->type == 11))
        {
            getMove(game->pieceList[i], game);
        }
    }
    getMove(game->pieceList[4], game);
    getMove(game->pieceList[28], game);
    getMove(game->pieceList[4], game); // repetition purposeful so white king gets reupdated on black king moves (which already sees white king moves)

    //get gamestate score
    double *dScores = getScore(orientation, game, depth, piece, turns);
    long score;
    long eScore;
    int checkmate = 0;
    int scale = depth + 1;
    if (scale > 4)
    {
        scale = 4;
    }
    if (dScores[0] == -88888.88888 && dScores[1] == 30.0)
    {
        score = LONG_MIN / scale;
    }
    else if (dScores[0] == 77.777 && dScores[1] == 77.7)
    {
        score += 100;
        checkmate = 1;
    }
    else if (dScores[0] == -77.777 && dScores[1] == -77.7)
    {
        score += -100;
        checkmate = -1;
    }
    else
    {
        score = (long)(dScores[0]);
    }

    eScore = (long)(dScores[1]);
    free(dScores);

    long *r = malloc(6 * sizeof(long));
    r[0] = oldLoc;
    r[1] = taken;
    r[2] = score;
    r[3] = eScore;
    r[4] = takenVal;
    r[5] = checkmate;
    return r;
}

void untestMove(int oldLoc, int taken, int orientation, Piece *piece, Gamestate *game)
{
    //decrement num moves
    piece->numMoves -= 1;

    //undo promotion if necessary
    if (oldLoc > 900)
    {
        oldLoc -= 900;
        if (orientation == 0)
        {
            piece->type = 1;
        }
        else
        {
            piece->type = 11;
        }
    }

    //return to old x,y
    int newX = piece->x;
    int newY = piece->y;
    int oldY = oldLoc % 10;
    int oldX = (oldLoc - oldY) / 10;
    game->board[oldY][oldX] = piece->ind;
    piece->x = oldX;
    piece->y = oldY;

    //replace taken piece
    if (taken != -1)
    {
        game->numAlive += 1;
        game->pieceList[taken]->alive = true;
        game->board[newY][newX] = taken;
        getMove(game->pieceList[taken], game);
    }
    else
    {
        game->board[newY][newX] = -1;
    }

    //recall getMove() for moving piece and all pieces listed as watching the tile moved to and tile moved away from (or pawns cause they don't watch but still depend on certain tiles -- could be more efficient here with another bitmap)
    if (piece->type != 6 && piece->type != 16)
    {
        getMove(piece, game);
    }

    for (int i = 0; i < 32; i++)
    {
        if (i != 4 && i != 28 && i != piece->ind && game->pieceList[i]->alive && (game->watchMap[newY][newX][i] != 0 || game->watchMap[oldY][oldX][i] != 0 || game->pieceList[i]->type == 1 || game->pieceList[i]->type == 11))
        {
            getMove(game->pieceList[i], game);
        }
    }
    getMove(game->pieceList[4], game);
    getMove(game->pieceList[28], game);
    getMove(game->pieceList[4], game); // repetition purposeful so white king gets reupdated on black king moves (which already sees white king moves)
}

int *getPlayerScoreDif(Gamestate *game, int orientation)
{
    int pieceWeights[6] = {1, 5, 3, 3, 9, 2};
    int yPScore = 0;
    int ePScore = 0;
    int maxAtRisk = -1;

    for (int i = 0; i < 32; i++)
    {
        Piece *piece = game->pieceList[i];
        if (piece->alive)
        {
            if (orientation == 1)
            {
                if (i > 15)
                {
                    int value = pieceWeights[piece->type - 11];
                    if (game->wAtt[piece->y][piece->x] > 0 && game->bAtt[piece->y][piece->x] > 0 && value > maxAtRisk)
                    {
                        //check if enemy pieces attacking this are worth trading
                        for (int j = 0; j < 16; j++)
                        {
                            if (game->watchMap[piece->y][piece->x][j] == 1)
                            {
                                Piece *attacker = game->pieceList[j];
                                if (attacker->alive && pieceWeights[attacker->type - 1] < value)
                                {
                                    maxAtRisk = value;
                                }
                            }
                        }
                    }
                    else if (game->wAtt[piece->y][piece->x] > 0 && value > maxAtRisk)
                    {
                        maxAtRisk = value;
                    }
                    yPScore += value;
                }
                else
                {
                    ePScore += pieceWeights[piece->type - 1];
                }
            }
            else
            {
                if (i > 15)
                {
                    ePScore += pieceWeights[piece->type - 11];
                }
                else
                {
                    int value = pieceWeights[piece->type - 1];
                    if (game->bAtt[piece->y][piece->x] > 0 && game->wAtt[piece->y][piece->x] > 0 && value > maxAtRisk)
                    {
                        //check if enemy pieces attacking this are worth trading
                        for (int j = 0; j < 16; j++)
                        {
                            if (game->watchMap[piece->y][piece->x][j + 16] == 1)
                            {
                                Piece *attacker = game->pieceList[j + 16];
                                if (attacker->alive && pieceWeights[attacker->type - 11] < value)
                                {
                                    maxAtRisk = value;
                                }
                            }
                        }
                    }
                    else if (game->bAtt[piece->y][piece->x] > 0 && game->wAtt[piece->y][piece->x] == 0 && value > maxAtRisk)
                    {
                        maxAtRisk = value;
                    }
                    yPScore += value;
                }
            }
        }
    }
    int *r = malloc(2 * sizeof(int));
    r[0] = yPScore - ePScore;
    r[1] = maxAtRisk;
    return r;
}

//get attacking / attacked bonus/penalty difference
int curBonus(Gamestate *game, int orientation)
{
    Piece *q = game->pieceList[27];
    Piece *eq = game->pieceList[3];
    Piece *r1 = game->pieceList[24];
    Piece *r2 = game->pieceList[31];
    Piece *er1 = game->pieceList[0];
    Piece *er2 = game->pieceList[7];
    Piece *k1 = game->pieceList[25];
    Piece *k2 = game->pieceList[30];
    Piece *ek1 = game->pieceList[1];
    Piece *ek2 = game->pieceList[6];
    Piece *b1 = game->pieceList[26];
    Piece *b2 = game->pieceList[29];
    Piece *eb1 = game->pieceList[2];
    Piece *eb2 = game->pieceList[5];
    int yPs = 0;
    int ePs = 0;

    for (int i = 0; i < 16; i++)
    {
        Piece *p = game->pieceList[8 + i];
        if (i < 8)
        {

            yPs += game->bAtt[p->y][p->x];
        }
        else
        {
            ePs += game->wAtt[p->y][p->x];
        }
    }
    int qdif;
    int rdif;
    int kdif;
    int bdif;
    int pdif;
    if (orientation == 1)
    {
        qdif = (game->bAtt[eq->y][eq->x] * 9) - (game->wAtt[q->y][q->x] * 9);
        rdif = ((game->bAtt[er1->y][er1->x] * 5) + (game->bAtt[er2->y][er2->x] * 5)) - ((game->wAtt[r1->y][r1->x] * 5) + (game->wAtt[r2->y][r2->x] * 5));
        kdif = ((game->bAtt[ek1->y][ek1->x] * 3) + (game->bAtt[ek2->y][ek2->x] * 3)) - ((game->wAtt[k1->y][k1->x] * 3) + (game->wAtt[k2->y][k2->x] * 3));
        bdif = ((game->bAtt[eb1->y][eb1->x] * 3) + (game->bAtt[eb2->y][eb2->x] * 3)) - ((game->wAtt[b1->y][b1->x] * 3) + (game->wAtt[b2->y][b2->x] * 3));
        pdif = yPs - ePs;
    }
    else
    {
        qdif = (game->wAtt[q->y][q->x] * 9) - (game->bAtt[eq->y][eq->x] * 9);
        rdif = ((game->wAtt[r1->y][r1->x] * 5) + (game->wAtt[r2->y][r2->x] * 5)) - ((game->bAtt[er1->y][er1->x] * 5) + (game->bAtt[er2->y][er2->x] * 5));
        kdif = ((game->wAtt[k1->y][k1->x] * 3) + (game->wAtt[k2->y][k2->x] * 3)) - ((game->bAtt[ek1->y][ek1->x] * 3) + (game->bAtt[ek2->y][ek2->x] * 3));
        bdif = ((game->wAtt[b1->y][b1->x] * 3) + (game->wAtt[b2->y][b2->x] * 3)) - ((game->bAtt[eb1->y][eb1->x] * 3) + (game->bAtt[eb2->y][eb2->x] * 3));
        pdif = ePs - yPs;
    }

    return (qdif + rdif + kdif + bdif + pdif);
}

bool kingAttacked(Gamestate *game, int orientation)
{
    if (orientation == 1)
    {
        Piece *king = game->pieceList[28];
        if (game->wAtt[king->y][king->x] > 0)
        {
            return true;
        }
    }
    else
    {
        Piece *king = game->pieceList[4];
        if (game->bAtt[king->y][king->x] > 0)
        {
            return true;
        }
    }
    return false;
}

bool isQueenTrapped(int orientation, Gamestate *game)
{
    Piece *q;
    bool attacked = false;
    bool trapped = false;
    if (orientation == 1)
    {
        q = game->pieceList[27];
        if (game->wAtt[q->y][q->x] > 0)
        {
            attacked = true;
        }
    }
    else
    {
        q = game->pieceList[3];
        if (game->bAtt[q->y][q->x] > 0)
        {
            attacked = true;
        }
    }
    if (!q->alive)
    {
        return false;
    }
    if (attacked)
    {
        for (int i = 0; i < q->moveset->used; i++)
        {
            int move = q->moveset->array[i];
            int my = move % 10;
            int mx = (move - my) / 10;
            if (orientation == 1)
            {
                if (game->wAtt[my][mx] == 0)
                {
                    return false;
                }
            }
            else
            {
                if (game->bAtt[my][mx] == 0)
                {
                    return false;
                }
            }
        }
        return true;
    }
    return false;
}

long leafSum(int orientation, Gamestate *game, int depth, int maxDepth, int turns)
{
    long long sum = 0;
    long long count = 0;
    Piece *yKing;
    //black or white
    int indOffset = 0;
    if (orientation == 1)
    {
        indOffset = 16;
        yKing = game->pieceList[28];
    }
    else
    {
        yKing = game->pieceList[4];
    }

    //tree
    //for each piece
    for (int i = 0; i < 16; i++)
    {
        Piece *piece = game->pieceList[i + indOffset];
        //only check moves if piece is alive
        if (piece->alive)
        {
            //for each move
            for (int j = 0; j < piece->moveset->used; j++)
            {
                count++;
                int move = piece->moveset->array[j];
                long *res = testMove(move, orientation, piece, game, turns, depth);
                int oldLoc = res[0];
                int taken = res[1];
                long score = res[2];
                int checkmate = res[5];
                free(res);

                //if leaf, add score to sum
                if (depth + 1 > maxDepth)
                {
                    if (!((orientation == 0 && game->bAtt[yKing->y][yKing->x] > 0) || (orientation == 1 && game->wAtt[yKing->y][yKing->x] > 0)))
                    {
                        int checkOverflow = sum + score;
                        if (score > 0 && sum > 0 && checkOverflow < 0)
                        {
                            sum = LLONG_MAX;
                        }
                        else if (score < 0 && sum < 0 && checkOverflow > 0)
                        {
                            sum = LLONG_MIN + 1;
                        }
                        else
                        {
                            sum = checkOverflow;
                        }
                    }
                }
                //give very bad score if checkmate possible on opponents next turn
                else if (checkmate == -1 && depth == 1)
                {
                    return LLONG_MIN + 1;
                }
                //dont bother recursing on moves w regular check either
                else if ((orientation == 0 && game->bAtt[yKing->y][yKing->x] > 0) || (orientation == 1 && game->wAtt[yKing->y][yKing->x] > 0))
                {
                    sum += 0;
                }

                //otherwise recurse
                else
                {
                    int scaledLeaves = leafSum(1 - orientation, game, depth + 1, maxDepth, turns);
                    int checkOverflow = sum + scaledLeaves;

                    if (scaledLeaves > 0 && sum > 0 && checkOverflow < 0)
                    {
                        sum = LLONG_MAX;
                    }
                    else if (scaledLeaves < 0 && sum < 0 && checkOverflow > 0)
                    {
                        sum = LLONG_MIN + 1;
                    }
                    else
                    {
                        sum = checkOverflow;
                    }
                }

                untestMove(oldLoc, taken, orientation, piece, game);
            }
        }
    }
    //return average outcome from this gamestate
    if (count == 0)
    {
        count = 1;
    }

    return sum / count;
}

//search top level tree for immediate move info, then travel downward recursively
int *shallowTreeSearch(int orientation, Gamestate *game, int depth, int maxDepth, bool stuck, int turns, bool random)
{
    int *r = malloc(2 * sizeof(int));

    int bestPiece = -1;
    int bestMove = -1;
    int secondBestMove = -1;
    int secondBestPiece = -1;
    int emergencyPiece = -1;
    int emergencyMove = -1;
    int bestFreePiece = -1;
    int worstSeenRisk = -1;

    long bestEmergencyScore = LONG_MIN;
    long bestFirstScore = LONG_MIN;
    long secondBestScore = LONG_MIN;
    long usedScore = LONG_MIN;
    long long bestScore = LLONG_MIN;

    //black or white
    int indOffset = 0;
    if (orientation == 1)
    {
        indOffset = 16;
    }

    //for each piece
    for (int i = 0; i < 16; i++)
    {
        Piece *piece = game->pieceList[i + indOffset];
        //only check moves if piece is alive
        if (piece->alive)
        {
            //for each move
            for (int j = 0; j < piece->moveset->used; j++)
            {
                int move = piece->moveset->array[j];

                //pre move top level score
                //int preBonus = curBonus(game, orientation);
                int *preInfo = getPlayerScoreDif(game, orientation);
                int preScore = preInfo[0];
                int preWorstRisk = preInfo[1];
                //bool queenTrapped = isQueenTrapped(orientation, game);
                free(preInfo);

                //make move
                long *res = testMove(move, orientation, piece, game, turns, 0);
                int oldLoc = res[0];
                int taken = res[1];
                long curScore = res[2];
                int takenVal = res[4];
                int checkmate = res[5];
                free(res);

                //printf("*****move: %d\n", move);
                //printf("piece: %ld\n", piece->ind);
                //printf("curScore: %ld\n", curScore);

                bool inCheck = kingAttacked(game, orientation);

                //if checkmate, immediately use this move
                if (!inCheck && checkmate == 1)
                {
                    printf("**********checkmate**********");
                    untestMove(oldLoc, taken, orientation, piece, game);
                    r[0] = piece->ind;
                    r[1] = move;
                    return r;
                }

                //store best legal move (best move to use when avoiding cases where legal moves were wrongly pruned)
                if (!inCheck && curScore > bestEmergencyScore)
                {
                    emergencyMove = move;
                    emergencyPiece = piece->ind;
                    bestEmergencyScore = curScore;
                }

                //post move top level score
                int *postInfo = getPlayerScoreDif(game, orientation);
                int postScore = postInfo[0];
                int postWorstRisk = postInfo[1]; //highest value piece you could immediately lose by making this move
                free(postInfo);
                //int postBonus = curBonus(game, orientation);

                if (postWorstRisk > worstSeenRisk)
                {
                    worstSeenRisk = postWorstRisk;
                }

                //check for favorable trades
                int pieceProfit = 0;
                if (takenVal > bestFreePiece && !inCheck && (takenVal > postWorstRisk || (takenVal == postWorstRisk && curScore >= usedScore))) //make sure you don't have an at-risk piece which is worth more than the one being taken
                {
                    //printf("favorable trade found!\n");
                    bestFreePiece = takenVal;
                    bestMove = move;
                    bestPiece = piece->ind;
                    bestFirstScore = curScore;
                    usedScore = curScore;
                    if (postWorstRisk > -1)
                    {
                        pieceProfit = takenVal - postWorstRisk;
                    }
                    else
                    {
                        pieceProfit = takenVal;
                    }
                }

                long long sum = LLONG_MIN;
                //as much pruning as possible:
                //only do deeper search if:
                //  - current move doesn't have you in check, AND
                //  - there isn't a free piece queued to be taken instead, AND
                //  - current score is better than the score for best previous move found, AND
                //  - you don't risk unrecoverably losing more than a pawn, OR you are losing less than you were before making this move

                //printf("bestFirstScore: %ld\n", bestFirstScore);
                //printf("postWorstRisk: %d\n", postWorstRisk);
                //printf("freePiece: %d\n", takenVal);
                //printf("inCheck: %d\n", inCheck);

                if (!inCheck && (bestFreePiece == -1 || pieceProfit == 0) && ((curScore >= (usedScore)) || usedScore == LONG_MIN) && (postWorstRisk < 1 || postWorstRisk < preWorstRisk))
                {
                    //printf("Searching deeper...\n");
                    if (curScore >= bestFirstScore)
                    {
                        bestFirstScore = curScore;
                    }
                    //recurse down
                    sum = leafSum(1 - orientation, game, depth + 1, maxDepth, turns);
                }
                //keep track of best top level position rating

                //update best move seen so far
                if (sum > bestScore)
                {
                    //printf("this is new best.\n");
                    //update a backup move to use if we find we are stuck in a repeating move loop
                    secondBestMove = bestMove;
                    secondBestPiece = bestPiece;
                    secondBestScore = bestScore;

                    bestScore = sum - 1000;
                    bestMove = move;
                    bestPiece = piece->ind;
                    usedScore = curScore;
                }

                //undo move
                untestMove(oldLoc, taken, orientation, piece, game);
            }
        }
    }

    //avoid rare(?) case of pruned legal move
    if (bestPiece == -1 && bestMove == -1)
    {
        //printf("****emergency move******");
        bestPiece = emergencyPiece;
        bestMove = emergencyMove;
    }

    int randFactor = rand() % 101;
    //if AI playing vs itself, give it a 55% chance to use it's second best move, to keep games different
    if (random && randFactor > 55 && secondBestMove != -1 && bestFreePiece == -1 && worstSeenRisk == -1 && secondBestScore != LONG_MIN)
    {
        bestPiece = secondBestPiece;
        bestMove = secondBestMove;
    }

    //free AI v AI game from loop of same moves
    if (stuck && secondBestMove != -1)
    {
        bestPiece = secondBestPiece;
        bestMove = secondBestMove;
    }

    r[0] = bestPiece;
    r[1] = bestMove;
    printf("alive: %d\n", game->numAlive);
    return r;
}

//requires maxdepth > 0
int *treeSearch(int orientation, Gamestate *game, int depth, int maxDepth, int firstMove, int firstPiece, time_t firstTime, int firstOrientation, int turns)
{

    static int counter = 0;
    //init static best score/piece/move trackers
    static long bestScore = LONG_MIN;
    int bestFreePiece = -1;
    int bestFreePieceAttack = -1;
    int bestFreePieceMove = -1;
    static int bestPiece = -1;
    static int bestMove = -1;
    int eBestScore = INT_MIN;
    long leafSum = 0;
    if (depth == 0)
    {
        bestScore = LONG_MIN;
        bestPiece = -1;
        bestMove = -1;
    }

    //iterate through all pieces, all moves for each (later replace with multi armed bandit)
    //int piece;
    //int move;

    int indOffset = 0;
    if (orientation == 1)
    {
        indOffset = 16;
    }
    for (int i = 0; i < 16; i++)
    {

        //only check moves if piece is alive
        if (game->pieceList[i + indOffset]->alive)

        {
            Piece *piece = game->pieceList[i + indOffset];
            for (int j = 0; j < piece->moveset->used; j++)
            {
                int move = piece->moveset->array[j];

                //store first move/piece in path
                int iMove = firstMove;
                int iPiece = firstPiece;
                if (depth == 0)
                {
                    iMove = move;
                    iPiece = piece->ind;
                }

                //make move, recurse, unmake move
                long *res = testMove(move, orientation, piece, game, turns, depth);
                //perftimer
                //counter++;
                //if (counter % 200000 == 0)
                //{
                //printf("%d\n", counter);
                //time_t cur = time(NULL);
                //double dif = difftime(cur, firstTime);
                //printf("TIME: %f\n", dif);
                //}

                int curScore = res[2];
                int eScore = res[3];

                if (eScore > eBestScore)
                {
                    eBestScore = eScore;
                }
                int freePiece = res[4];
                if (depth == 0)
                {
                    int qInd = 3;
                    int qx = game->pieceList[qInd]->x;
                    int qy = game->pieceList[qInd]->y;
                    bool qAtt = false;
                    if (game->bAtt[qy][qx] > 0)
                    {
                        qAtt = true;
                    }
                    if (orientation == 1)
                    {
                        qAtt = false;
                        qInd = 27;
                        qx = game->pieceList[qInd]->x;
                        qy = game->pieceList[qInd]->y;
                        if (game->wAtt[qy][qx] > 0)
                        {
                            qAtt = true;
                        }
                    }
                    //prioritize capturing free pieces over primary score

                    if (freePiece > bestFreePiece && curScore != INT_MIN && (!qAtt || freePiece == 9))
                    {
                        bestFreePiece = freePiece;
                        bestFreePieceMove = move;
                        bestFreePieceAttack = piece->ind;
                    }
                }
                //optionally skip recursion if score is terrible? maybe nonviable since score could reverse drastically (try giving checkmates int_min, or also illegal moves slipping through)
                if (depth + 1 <= maxDepth && (depth != 1 || (depth == 1 && bestFreePiece == -1)))
                {

                    //enemy only pick good moves here
                    if (depth % 2 == 1)
                    {
                        if (eScore == eBestScore)
                        {
                            treeSearch(1 - orientation, game, depth + 1, maxDepth, iMove, iPiece, firstTime, firstOrientation, turns);
                        }
                    }
                    else
                    {
                        Piece *qTest = game->pieceList[27];
                        if (curScore > INT_MIN)
                        {
                            if (!qTest->alive || game->wAtt[qTest->y][qTest->x] == 0 || bestScore == INT_MIN)
                            {
                                treeSearch(1 - orientation, game, depth + 1, maxDepth, iMove, iPiece, firstTime, firstOrientation, turns);
                            }
                        }
                    }
                }
                //base case record leaf node score and add to leaf sum
                else
                {

                    leafSum += curScore;
                }
                untestMove(res[0], res[1], orientation, piece, game);
                free(res);
            }
        }
    }
    //if leaf sum is best seen so far, this is new best path to take
    if (depth == maxDepth)
    {
        if (leafSum >= bestScore)
        {
            bestScore = leafSum;
            bestPiece = firstPiece;
            bestMove = firstMove;
        }
    }
    if (depth != 0)
    {
        return NULL;
    }
    else
    {
        if (bestFreePiece > -1)
        {
            bestMove = bestFreePieceMove;
            bestPiece = bestFreePieceAttack;
        }
        int *r = malloc(3 * sizeof(int));
        r[0] = bestPiece;
        r[1] = bestMove;
        r[2] = bestScore;
        return r;
    }
}

//piece data = [piece ids 0-32, bottom to top, left to right, white black][ x, y, alive (0||1), nummoves, type, pieceIndex]
Gamestate *initGamestate(int pieceData[32][6], bool zeroPlayer)
{

    Gamestate *g = malloc(sizeof(Gamestate));
    if (g == NULL)
    {
        return NULL;
    }
    g->zeroPlayer = zeroPlayer;

    //init watch trackers
    memset(g->watchMap, 0, sizeof(g->watchMap));
    memset(g->bAtt, 0, sizeof(g->bAtt));
    memset(g->wAtt, 0, sizeof(g->wAtt));

    //init piece objects
    for (int i = 0; i < 32; i++)
    {
        Piece *piece = initPiece(pieceData[i]);
        g->pieceList[i] = piece;
    }

    //init board of -1
    memset(g->board, -1, sizeof(g->board));

    //init pieces on board
    int na = 0;

    for (int i = 0; i < 32; i++)
    {

        if (g->pieceList[i]->alive)
        {
            na += 1;
            int x = g->pieceList[i]->x;
            int y = g->pieceList[i]->y;
            g->board[y][x] = i;
        }
    }
    g->numAlive = na;

    //fill piece movesets (avoid king until last so it can see all watches)
    for (int i = 0; i < 32; i++)
    {
        if (i != 4 && i != 28 && g->pieceList[i]->alive)
        {
            getMove(g->pieceList[i], g);
        }
    }
    //fetch king moves
    getMove(g->pieceList[4], g);
    getMove(g->pieceList[28], g);
    return g;
}

void freeGamestate(Gamestate *game)
{
    for (int i = 0; i < 32; i++)
    {
        freePiece(game->pieceList[i]);
    }
    free(game);
}

void AIvAI()
{
    FILE *fTurn;
    FILE *fMove;
    FILE *fGame;
    Gamestate *game;
    int turn = 0;
    int pieceData[32][6];

    //init random factor for moves
    srand((unsigned)time(NULL));

    //repeated move tracker
    int recentPositions[6] = {-1, -1, -1, -1, -1, -1};
    int recentPieces[6] = {-1, -1, -1, -1, -1, -1};

    bool run = true;
    bool first = true;
    int orientation = 0;
    int turns = 0;
    while (run)
    {
        //wait for python to be ready
        while (turn == 0)
        {
            Sleep(400);
            fTurn = fopen("turn.txt", "r");
            fscanf(fTurn, "%d", &turn);
            fclose(fTurn);
        }

        //init gamestate
        if (first)
        {
            first = false;
            fGame = fopen("gamestate.txt", "r");
            for (int i = 0; i < 32; i++)
            {
                for (int j = 0; j < 6; j++)
                {
                    int num;
                    fscanf(fGame, "%d", &num);
                    pieceData[i][j] = num;
                }
            }
            fclose(fGame);
            game = initGamestate(pieceData, true);
        }

        for (int i = 0; i < 8; i++)
        {
            for (int j = 0; j < 8; j++)
            {
                int num = game->board[i][j];
                if (num >= 0 && num < 10)
                {
                    printf(" %d ", num);
                }
                else
                {
                    printf("%d ", num);
                }
            }
            printf("\n");
        }
        printf("\n");

        turns++;
        int cMaxDepth = 3;
        if (game->numAlive < 8)
        {
            cMaxDepth = 4;
        }

        //detect repetition (and prevent infinite move loop)
        bool stuck = false;
        if (recentPositions[0] != -1)
        {
            if (recentPositions[0] == recentPositions[4] && recentPositions[1] == recentPositions[5])
            {
                if (recentPieces[0] == recentPieces[2] && recentPieces[2] == recentPieces[4] && recentPieces[1] == recentPieces[3] && recentPieces[3] == recentPieces[5])
                {
                    stuck = true;
                }
            }
        }

        //find move
        int *best = shallowTreeSearch(orientation, game, 0, cMaxDepth, stuck, turns, true);
        printf("orientation: %d, piece: %d, move: %d \n", orientation, best[0], best[1]);
        if (best[0] != -1)
        {
            testMove(best[1], orientation, game->pieceList[best[0]], game, turns, 0);
            orientation = 1 - orientation;
            int rPosition = game->pieceList[best[0]]->x * 10 + game->pieceList[best[0]]->y;
            //arbitrarily unrolled loop O.O
            recentPositions[0] = recentPositions[1];
            recentPositions[1] = recentPositions[2];
            recentPositions[2] = recentPositions[3];
            recentPositions[3] = recentPositions[4];
            recentPositions[4] = recentPositions[5];
            recentPositions[5] = rPosition;
            recentPieces[0] = recentPieces[1];
            recentPieces[1] = recentPieces[2];
            recentPieces[2] = recentPieces[3];
            recentPieces[3] = recentPieces[4];
            recentPieces[4] = recentPieces[5];
            recentPieces[5] = best[0];
        }

        //send move to file for python to update GUI
        fMove = fopen("move.txt", "w+");
        if (best[2] == INT_MIN)
        {
            fprintf(fMove, "%d ", -1);
            fprintf(fMove, "%d", -1);
        }
        else
        {
            fprintf(fMove, "%d ", best[0]);
            fprintf(fMove, "%d", best[1]);
        }

        fclose(fMove);
        free(best);

        //change turns
        fTurn = fopen("turn.txt", "w+");
        fprintf(fTurn, "%d", 0);
        fclose(fTurn);
        turn = 0;
    }
}

//given a gamestate from gamestate.txt, writes the best move for the AI to make as <piece, move_location> to move.txt
void AI()
{

    int pieceData[32][6];

    //file setup
    FILE *fTurn;
    FILE *fGame;
    FILE *fMove;

    int turn = 0;

    //main waitloop (while python executes)
    bool run = true;
    static int turns = 0;
    while (run)
    {
        //while not the AI's turn, wait and check if it becomes AI's turn
        while (turn == 0)
        {
            Sleep(1000);
            fTurn = fopen("turn.txt", "r");
            fscanf(fTurn, "%d", &turn);
            fclose(fTurn);
        }

        //read gamestate loop
        fGame = fopen("gamestate.txt", "r");
        for (int i = 0; i < 32; i++)
        {
            for (int j = 0; j < 6; j++)
            {
                int num;
                fscanf(fGame, "%d", &num);
                pieceData[i][j] = num;
            }
        }
        fclose(fGame);

        //init gamestate from what was read
        Gamestate *game = initGamestate(pieceData, false);

        //perf timer
        time_t start = time(NULL);

        turns++;
        int cMaxDepth = 3;
        if (game->numAlive < 12)
        {
            cMaxDepth = 4;
        }

        for (int i = 0; i < 8; i++)
        {
            for (int j = 0; j < 8; j++)
            {
                int num = game->bAtt[i][j];
                if (num >= 0 && num < 10)
                {
                    printf(" %d ", num);
                }
                else
                {
                    printf("%d ", num);
                }
            }
            printf("\n");
        }
        printf("\n");

        //find and write [bestPiece, bestMove]
        printf("depth: %d\n", cMaxDepth);
        int *best = shallowTreeSearch(1, game, 0, cMaxDepth, false, turns, false);
        printf("piece: %d move: %d \n", best[0], best[1]);
        fMove = fopen("move.txt", "w+");
        if (best[2] == INT_MIN)
        {
            fprintf(fMove, "%d ", -1);
            fprintf(fMove, "%d", -1);
        }
        else
        {
            fprintf(fMove, "%d ", best[0]);
            fprintf(fMove, "%d", best[1]);
        }

        fclose(fMove);

        //change turns
        fTurn = fopen("turn.txt", "w+");
        fprintf(fTurn, "%d", 0);
        fclose(fTurn);
        turn = 0;
        //free all used memory
        freeGamestate(game);
        Sleep(800);
    }
}

int test(int data[32][6])
{
    printf("test\n");
    return data[15][5];
}

int main(int argc, char *argv[])
{
    char onePlayerMode[] = "1";
    if (strcmp(argv[1], onePlayerMode) == 0)
    {
        AI();
    }
    else
    {
        AIvAI();
    }

    return 0;
}