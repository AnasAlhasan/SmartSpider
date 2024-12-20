from run_spiders import RunSpiders
from data_processing import process_and_save



if __name__ == '__main__':
    x = input()
    RunSpiders(x)
    process_and_save(x)
    