import ptt_parser
import pymongo


def update_board_list(list):
	conn=pymongo.Connection('127.0.0.1',27017)

	db = conn['setting']
	db.board_list.drop()
	for board_name in list:
		db.board_list.insert({'board':board_name})

def update_board_data():
	board_list = ['Gossiping', 'beauty', 'joke', 'StupidClown', 'sex']

	parser = ptt_parser.PttWebParser()
	# parser.board_parse('Gossiping', 24)
	# parser.board_parse('beauty', 24)
	# parser.board_parse('joke', 24)
	# parser.board_parse('StupidClown', 24)
	parser.board_parse('sex', 24)
	parser.board_parse('PublicIssue', 24)
	parser.board_parse('HatePolitics', 24)
	update_board_list(board_list)		

if __name__ == "__main__":

	update_board_data()
