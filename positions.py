def positions(piece, source, oldPos, target, action):
    possibilities = [source]

    def vertical(start, arrival, step, letter):
        for i in range(start, arrival, step):
            position = letter + str(i)
            if any(position in dic for dic in oldPos):
                pieceOnTarget = oldPos[position]
                if piece[0] == pieceOnTarget[0]:
                    break
                else:
                    possibilities.append(letter + str(i))
                    break
            else:
                possibilities.append(letter + str(i))

    def horizontal(start, arrival, step, number):
        for i in range(start, arrival, step):
            position = str(chr(i)) + str(number)
            if any(position in dic for dic in oldPos):
                    pieceOnTarget = oldPos[position]
                    if piece[0] == pieceOnTarget[0]:
                        break
                    else:
                        possibilities.append(chr(i) + str(number))
            else:
                possibilities.append(chr(i) + str(number))
    
    def diagonal(letter, number, movement):
        for i in range(1, 8):
            if movement == "first":
                position = chr(ord(letter) + i) + str(int(number) + i)
            elif movement == "forth":
                position = chr(ord(letter) + i) + str(int(number) - i)
            elif movement == "second":
                position = chr(ord(letter) - i) + str(int(number) + i)
            elif movement == "third":
                position = chr(ord(letter) - i) + str(int(number) - i)
            
            if not any(position in dic for dic in oldPos):
                possibilities.append(position)
            else:
                pieceOnTarget = oldPos[position]
                if piece[0] == pieceOnTarget[0]:
                    break
                else:
                    possibilities.append(position)
                    break

    def bishop_movement(letter, number):
        diagonal(letter, number, movement="first")
        diagonal(letter, number, movement="second")
        diagonal(letter, number, movement="third")
        diagonal(letter, number, movement="forth")
        
    def rook_movement(letter, number):
        vertical(int(number)+1, 9, 1, letter)
        vertical(int(number)-1, 0, -1, letter)
        
        horizontal(ord(letter)+1, 105, 1, number)
        horizontal(ord(letter)-1, 96, -1, number)
    
    def check_piece(position):
            if not any(position in dic for dic in oldPos):
                    possibilities.append(position)
            else:
                pieceOnTarget = oldPos[position]
                if piece[0] != pieceOnTarget[0]:
                    possibilities.append(position)


    #looking for all the possible movements for a pawn at that case
    if piece[1] == "P":
        #for the movement
        if action == "get_movement":
            if source[1] == "2" or source[1] == "7":
                if piece[0] == "w":
                    vertical(int(source[1])+1, int(source[1])+3, 1, source[0])
                elif piece[0] == "b":
                    vertical(int(source[1])-1, int(source[1])-3, -1, source[0])
            else:
                if piece[0] == "w":
                    vertical(int(source[1])+1, int(source[1])+2, 1, source[0])
                elif piece[0] == "b":
                    vertical(int(source[1])-1, int(source[1])-2, -1, source[0])
        
        if action == "get_movement":
            if piece[0] == "w":
                position = source[0] + str(int(source[1]) + 1)
                if any(position in dic for dic in oldPos):
                    possibilities.remove(position)
            if piece[0] == "b":
                position = source[0] + str(int(source[1]) - 1)
                if any(position in dic for dic in oldPos):
                    possibilities.remove(position)
        
        #in order to eat
        if piece[0] == "w":
            for i in range(-1, 2, 2):
                position = chr(ord(source[0]) + i) + str(int(source[1]) + 1)
                possibilities.append(position)
        elif piece[0] == "b":
            for i in range(-1, 2, 2):
                position = chr(ord(source[0]) + i) + str(int(source[1]) - 1)
                possibilities.append(position)


    #looking for all the possible movements for a rook at that case
    elif piece[1] == "R":
        rook_movement(source[0], source[1])
        
    #looking for all the possible movements for a knight at that case

    elif piece[1] == "N":
        for i in range(2, -3, -1):
            if i == 2 or i == -2:
                check_piece(str( chr( ord( source[0]) + 1)) + str(int(source[1]) + i))
                check_piece(str( chr( ord( source[0]) - 1)) + str(int(source[1]) + i))
            elif i == 1 or i == -1:
                check_piece(str(chr(ord( source[0]) - 2)) + str(int(source[1]) + i))
                check_piece(str( chr( ord (source[0]) + 2)) + str(int(source[1]) + i))
    
    
    #looking for all the possible movements for a king at that case
    elif piece[1] == "K":
        for i in range(-1, 2):
            for x in range(-1, 2):
                possibilities.append(str( chr( ord( source[0]) + x)) + str(int(source[1]) + i))
        if check_check(piece, oldPos, source, target):
            return "illegal play"

    
    #looking for all the possible movements for a bishop at that case
    elif piece[1] == "B":
        bishop_movement(source[0], source[1])

    #looking for all the possible movements for a queen at that case
    elif piece[1] == "Q":
        bishop_movement(source[0], source[1])
        rook_movement(source[0], source[1])

    return possibilities

def check_check(piece, oldPos, source, target):
    target_case = target
    print(oldPos)
    for i in oldPos:
        if oldPos[i][0] != piece[0] and oldPos[i][1] != "K":
            possibilities = positions(oldPos[i], i, oldPos, target, "baz")
            if target_case in possibilities:
                return True
    return False
            