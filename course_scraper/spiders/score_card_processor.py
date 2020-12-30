"""
Defining a python functions that handle the processing of the score card
"""
import re


def chunks(lst, n):
    """Yield successive n-sized chunks from list (lst).
    This is used to break the distances into n number of seperate lists of dictionaries
    """
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def compile_tee_cr_slope(response):
    """ This function takes in the page response for the scorecard
    Process:
        - Create 3 empty lists for the course rating (cr), slope, and tee color
        - Gather the text values of from the response
        - split the values by ' /' into 3 groups
        - iterate over the list to create 3 dictionaries
            - tee: str
            - rating: int
            - slope: int
        - Combine the 3 dictionaries together for one list of dictionaries

    Return:
        - A list of dictionaroes
    """
    cr = []
    slopes = []
    tees = []

    # Gather the raw text
    tees_cr_slopes_group = response.xpath(
        "normalize-space((//div[not(@id) and not(@class)]/text())[2])").get()

    # Split the values into 3 seperate parts. Tee, Rating, Slope
    tees_cr_slopes_split = [
        x.strip(r' /') for x in re.split(r"\||\s(?=\d)", tees_cr_slopes_group)]

    for v, k in list(zip((["rating"] * len(tees_cr_slopes_split[2::3])), tees_cr_slopes_split[2::3])):
        cr.append({v: k})

    for v, k in list(zip((["slope"] * len(tees_cr_slopes_split[2::3])), tees_cr_slopes_split[1::3])):
        slopes.append({v: k})

    for v, k in list(zip((["tees"] * len(tees_cr_slopes_split[2::3])), tees_cr_slopes_split[0::3])):
        tees.append({v: k})

    # Combine into a list of dictionaries like {Rating: '', Slope: ''}
    [k.update(v) for k, v in list(zip(cr, slopes))]

    # Combine into a list of dictionaries like {Tees: '', Rating: '', Slope: ''}
    [k.update(v) for k, v in list(zip(tees, cr))]

    return tees


def compile_distances_holes(response):
    """ This function takes in the page response for the scorecard
    Process:
        - Create 2 empty lists for the holes and distances
            - Holes will be a list of dictionaries
                - Hole: int
                - Index: str
                - Par: int
        - Gather the table and the rows from the response

    Return:
        - A list of dictionaries
    """
    holes = []
    distances = []

    table = response.xpath("(.//table)[1]")
    rows = table.xpath(".//tr")
    distance_rows = rows[3:]

    # I know that the value for each scorecard is from range 2 - 23 or 1 - 22 ty
    for i in range(2, 23):
        """ Gather the rows by position
        The first 3 rows are always hole, index, par
        Then use the iterator to gather the other columns
        """
        values = {
            table.xpath(".//tr[1]/td/text()").get().lower(): table.xpath(".//tr[1]/td["+str(i)+"]/text()").get(),
            table.xpath(".//tr[2]/td/text()").get().lower(): table.xpath(".//tr[2]/td["+str(i)+"]/text()").get(),
            table.xpath(".//tr[3]/td/text()").get().lower(): table.xpath(".//tr[3]/td["+str(i)+"]/text()").get(),
        }
        holes.append(values)

    for distance in distance_rows.xpath(".//td"):
        """ Gather all of the distances
        This function gathers all of the distances and passes on the text for the tee names
        """
        try:
            values = {}
            values['distance'] = int(
                re.sub(r'<.+?>|\n|\r| ', '', distance.xpath(".//text()").get().lower()))
        except:
            pass

        if values:
            distances.append(values)
    """ This zips the two dictionaries together into one based on the number of tees on the scorecard """
    for k, v in list(zip(distances, holes * len(distance_rows))):
        k.update(v)

    score_card_distances = list(chunks(distances, 21))

    return score_card_distances


def create_scorecard(response):
    """
    Calls the other functions that then create the score card
    """

    tees = compile_tee_cr_slope(response)
    score_card_distances = compile_distances_holes(response)

    for k, v in list(zip(tees, score_card_distances)):
        k.update({'tee_holes': v})

    # There was an issue with some arrays containing 'None' and were not replaced with ""
    # tees_data = json.dumps(tees).replace('null', '""')

    return tees
