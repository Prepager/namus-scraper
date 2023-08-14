import os, json, grequests, requests, functools

SEARCH_LIMIT = 10000
REQUEST_BATCH_SIZE = 50
REQUEST_FEEDBACK_INTERVAL = 50

USER_AGENT = "NamUs Scraper / github.com/prepager/namus-scraper"
API_ENDPOINT = "https://www.namus.gov/api"
STATE_ENDPOINT = API_ENDPOINT + "/CaseSets/NamUs/States"
CASE_ENDPOINT = API_ENDPOINT + "/CaseSets/NamUs/{type}/Cases/{case}"
SEARCH_ENDPOINT = API_ENDPOINT + "/CaseSets/NamUs/{type}/Search"

DATA_OUTPUT = "./output/{type}/{type}.json"
CASE_TYPES = {
    "MissingPersons": {"stateField": "stateOfLastContact"},
    "UnidentifiedPersons": {"stateField": "stateOfRecovery"},
    "UnclaimedPersons": {"stateField": "stateFound"},
}

completedCases = 0


def main():
    print("Fetching states\n")
    states = requests.get(STATE_ENDPOINT, headers={"User-Agent": USER_AGENT}).json()

    for caseType in CASE_TYPES:
        output_dict = dict()

        print("Collecting: {type}".format(type=caseType))

        global completedCases
        completedCases = 0

        print(" > Fetching case identifiers")
        searchRequests = (
            grequests.post(
                SEARCH_ENDPOINT.format(type=caseType),
                headers={"User-Agent": USER_AGENT, "Content-Type": "application/json"},
                data=json.dumps(
                    {
                        "take": SEARCH_LIMIT,
                        "projections": ["namus2Number"],
                        "predicates": [
                            {
                                "field": CASE_TYPES[caseType]["stateField"],
                                "operator": "IsIn",
                                "values": [state["name"]],
                            }
                        ],
                    }
                ),
            )
            for state in states
        )

        searchRequests = grequests.map(searchRequests, size=REQUEST_BATCH_SIZE)
        cases = functools.reduce(
            lambda output, element: output + element.json()["results"],
            searchRequests,
            [],
        )

        print(" > Found %d cases" % len(cases))

        print(" > Creating output file")
        filePath = DATA_OUTPUT.format(type=caseType)
        os.makedirs(os.path.dirname(filePath), exist_ok=True)
        #outputFile = open(filePath, "w")
        #outputFile.write("[")

        print(" > Starting case processing")
        caseRequests = (
            grequests.get(
                CASE_ENDPOINT.format(type=caseType, case=case["namus2Number"]),
                hooks={"response": requestFeedback},
                headers={"User-Agent": USER_AGENT},
            )
            for case in cases
        )

        caseRequests = grequests.map(caseRequests, size=REQUEST_BATCH_SIZE)
        for index, case in enumerate(caseRequests):
            if not case:
                print(
                    " > Failed parsing case: {case} index {index}".format(
                        case=cases[index], index=index
                    )
                )
                continue

            #outputFile.write(
            #    case.text + ("," if ((index + 1) != len(caseRequests)) else "")
            #)
            tem_output = json.loads(case.text)
            output_dict[tem_output["id"]] = tem_output

        print(" > Closing output file")
        #outputFile.write("]")
        #outputFile.close()
        with open(filePath, "w") as outfile:
            json.dump(output_dict, outfile)
        

    print("Scraping completed")


def requestFeedback(response, **kwargs):
    global completedCases
    completedCases = completedCases + 1

    if completedCases % REQUEST_FEEDBACK_INTERVAL == 0:
        print(" > Completed {count} cases".format(count=completedCases))


main()
