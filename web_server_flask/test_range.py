import data_to_range
import track_data_stats
import json
from desktop import pirail
def main():

    #data_to_range.write_json_data_to_range('data/test.json', 'data/sample.json', 6.9, 6.9798537873105815)
    #track_data_stats.write_average_json_file('data/test.json', 'data/test_stats.json')
    #track_data_stats.write_std_json_file('data/test.json', 'data/test_stats.json')
    track_data_stats.dump('data/test.json', 'data/test_stats.json')

if __name__ == '__main__':
    main()
