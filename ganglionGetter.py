import argparse
import time

from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds, BrainFlowPresets


def main():
    BoardShim.enable_dev_board_logger()

    params = BrainFlowInputParams()
    params.serial_port = "COM6"
    board = BoardShim(BoardIds.GANGLION_BOARD, params)
    
    # params.ip_port = args.ip_port
    # params.serial_port = args.serial_port
    # params.mac_address = args.mac_address
    # params.other_info = args.other_info
    # params.serial_number = args.serial_number
    # params.ip_address = args.ip_address
    # params.ip_protocol = args.ip_protocol
    # params.timeout = args.timeout
    # params.file = args.file
    # params.master_board = args.master_board

    # board = BoardShim(args.board_id, params)
    board.prepare_session()
    board.start_stream ()
    time.sleep(10)
    # data = board.get_current_board_data (256) # get latest 256 packages or less, doesnt remove them from internal buffer
    data = board.get_board_data()  # get all data and remove it from internal buffer
    board.stop_stream()
    board.release_session()

    print(data)


if __name__ == "__main__":
    main()