
# Read in jobs from the _data/jobs.yml file, file links that are both
# expired and not working, and remove them. Write to a new file.
# Copyright @vsoch, 2020

import os
import datetime
from urlchecker.core.urlproc import check_urls
import shutil
import sys
import tempfile
import yaml

here = os.path.dirname(os.path.abspath(__file__))

def get_filepath():
    '''load the jobs file.
    '''
    filepath = os.path.join(os.path.dirname(here), '_data', 'jobs.yml')

    # Exit on error if we cannot find file
    if not os.path.exists(filepath):
        print("Cannot find %s" % filepath)

    return filepath

def read_jobs(filepath):
    '''read in the jobs data.
    '''
    # Read in the entire membership counts
    with open(filepath, 'r') as fd:
        data = yaml.load(fd.read(), Loader=yaml.SafeLoader)
    return data


def main():
    '''a small helper to update the _data/memberCounts.csv file.
    '''
    # We will read through file, and write entry for current month.
    filepath = get_filepath()

    # Read in the jobs
    jobs = read_jobs(filepath)

    # Keep a list to re-write to file
    keepers = []

    # Use the same urlchecker function for consistency
    now = datetime.date.today()

    for job in jobs:

        # We don't check urls that are not expired, the urlchecker action should
        # catch these and fail
        if job['expires'] > now:
            print("Skipping %s, expires in future." % job['name'])
            keepers.append(job)
            continue

        check_results = {"failed": [], "passed": []}
        check_urls(urls=[job['url']], retry_count=3, timeout=5, check_results=check_results) 
 
        # If the url passes, add to keepers
        if check_results['passed']:
            keepers.append(job)
        else:
            print("%s is expired and did not pass, not adding back to jobs." % job['url'])

        # Finally, update data file
    _, tmpfile = tempfile.mkstemp(prefix='jobs-', suffix=".yml")

    # Write the new file
    with open(tmpfile, 'w') as outfile:
        yaml.dump(keepers, outfile)

    # Copy finished file - will need to be added in pull request
    shutil.copyfile(tmpfile, filepath)  

if __name__ == '__main__':
    main()
