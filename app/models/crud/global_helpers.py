




def get_most_recent_entry(inlist):

    inlist.sort(key=lambda x: x.updated, reverse=True)
    if len(inlist) > 0:
        return inlist[0]

    return None


