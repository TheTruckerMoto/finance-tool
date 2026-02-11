import csv

def laad_data(bestandsnaam):
    print(f"Start met lexen van {bestandsnaam}...")

    # Make emty list
    transacties = []

    # Read file (Read only because of 'r' temp file name f)
    with open (bestandsnaam, mode='r') as f:

        # Nakijekn wat een dictreader exact is..
        lezer = csv.DictReader(f)

        # Make loop 
        for regel in lezer:
            # Makes a list that appends
            transacties.append(regel)

    # Gives info to function
    return transacties        

# start actions from function
if __name__ == "__main__":

    mijn_data = laad_data("dummy.csv")

    aantal = len(mijn_data)

    # Console output
    print(f"Gevonden transacties: {aantal}")

    # Console output 1st
    print("De eerste is:", mijn_data[0])

