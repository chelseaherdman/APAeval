#!/usr/bin/env python3

from __future__ import division, print_function
import pandas
import os, json
import sys
from argparse import ArgumentParser
from JSON_templates import JSON_templates

parser = ArgumentParser()
parser.add_argument("-i", "--participant_data", help="list of cancer genes prediction", required=True)
parser.add_argument("-com", "--community_name", help="name of benchmarking community", required=True)
parser.add_argument("-c", "--challenge_types", nargs='+', help="list of types of cancer selected by the user, separated by spaces", required=True)
parser.add_argument("-p", "--participant_name", help="name of the tool used for prediction", required=True)
parser.add_argument("-r", "--public_ref_dir", help="directory with the list of cancer genes used to validate the predictions", required=True)
parser.add_argument("-o", "--output", help="output path where participant JSON file will be written",
                    required=True)

args = parser.parse_args()


def main(args):

    # input parameters
    input_participant = args.participant_data
    public_ref_dir = args.public_ref_dir
    community = args.community_name
    challenges = args.challenge_types
    participant_name = args.participant_name
    out_path = args.output

    # Assuring the output path does exist
    if not os.path.exists(os.path.dirname(out_path)):
        try:
            print(os.path.dirname(out_path))
            os.makedirs(os.path.dirname(out_path))
            with open(out_path, mode="a") : pass
        except OSError as exc:
            print("OS error: {0}".format(exc) + "\nCould not create output path: " + out_path)

    validate_input_data(input_participant, public_ref_dir, community, challenges, participant_name, out_path)



def  validate_input_data(input_participant,  public_ref_dir, community, challenges, participant_name, out_path):
    # get participant predicted genes
    try:
        participant_data = pandas.read_csv(input_participant, sep='\t',
                                           comment="#", header=0)
    except:
        sys.exit("ERROR: Submitted data file {} is not in a valid format!".format(input_participant))
    
    methods_ran = [method_and_sample.split()[0] for method_and_sample in list(participant_data.iloc[:, 3].values)]
    print(methods_ran)
    # get ids of the submited fields   ##bed does not have header
#    data_fields = ['chrom', 'chromStart', 'chromEnd', 'name', 'score', 'strand']
#    submitted_fields = list(participant_data.columns.values)
    
    # get reference dataset to validate against
    validated = False
    for public_ref_rel in os.listdir(public_ref_dir):
        public_ref = os.path.join(public_ref_dir,public_ref_rel)
        if os.path.isfile(public_ref):
            try:
                public_ref_data = pandas.read_csv(public_ref, sep='\t',
                                                  comment="#", header=0)
                methods_check = list(public_ref_data.iloc[:, 0].values)
                #print([method for method in methods_ran])
                ## validate the fields of the submitted data and if the predicted genes are in the mutations file
                if [method in methods_check for method in methods_ran].count(False) == 0:
                    validated = True
                else:
                    print("WARNING: Submitted data does not validate against "+public_ref,file=sys.stderr)
                    validated = False
            except:
                print("PARTIAL ERROR: Unable to properly process "+public_ref,file=sys.stderr)
                import traceback
                traceback.print_exc()

    data_id = community + ":" + participant_name + "_P"
    output_json = JSON_templates.write_participant_dataset(data_id, community, challenges, participant_name, validated)

    # print file

    with open(out_path , 'w') as f:
        json.dump(output_json, f, sort_keys=True, indent=4, separators=(',', ': '))

    if validated == True:

        sys.exit(0)
    else:
        sys.exit("ERROR: Submitted data does not validate against any reference data! Please check " + out_path)


if __name__ == '__main__':

    main(args)
