from monopoly.db import get_db


class Monopoly_map:
    def __init__(self):
        db = get_db()
        self.__map = db.execute(
            'SELECT *'
            ' FROM map'
        ).fetchall()

    def get_current_cell(self, position):
        for cell in self.__map:
            if cell['index'] == position:
                return cell

    def get_map(self):
        return self.__map


def Monopoly(list_of_data):
    for player_data in list_of_data:
        turn = player_data['turn'] # не существует 'turn'
        if turn:
            user = player_data['user']
            status = player_data['status'] #jailed - 01/02/03, free - 1
            balance = player_data['balance']
            dices = [random.randint(1, 6), random.randint(1, 6)]
            if not bool(status[0]):
                if dices[0] != dices[1]:
                    status = status[0] + str(int(status[1]) + 1)
                    if status[1] == '3':
                        message = messages['pay_to_escape']
                        balance-=50
                        status = '1'
                else:
                    status='1'

            if bool(status[0]):

                position = player_data['position']
                next_position = position + sum(dice)
