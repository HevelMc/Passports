import requests, json, datetime, os, asyncio, csv
from telegram import Bot
bot = None

nint = lambda input: None if input == "null" else int(input)

async def send_requests():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0;Win64;x64;rv:101.0) Gecko/20100101 Firefox/101.0',
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
    }

    dates = []

    with open("data.json", "r") as f:
        data = json.load(f)
        city_name = data["city-name"]
        city_postal = data["city-postal"]
        precmd_id = data["pre-cmd-id"]
        telegram_user_id = data["telegram-user-id"]

    with open("data.csv", "r") as f:
        # read the data from the file, the first line is the header
        reader = csv.DictReader(f, delimiter=";", quotechar="\"", quoting=csv.QUOTE_ALL)

        for row in reader:
            print("mairie: " + str(row["id_professional_company"]))

            data = {
                "transaction_id": "",
                "id_professional_company": nint(row["id_professional_company"]),
                "id_professional_agenda": nint(row["id_professional_agenda"]),
                "id_professional_prestation": nint(row["id_professional_prestation"]),
                "id_professional_place": [int(p) for p in row["id_professional_place"].split(",")],
                "source_type":"widget",
                "duration":7,
                "number_slots":1,
                "display_time_slots_as_range": False,
                "additional_informations_start":
                    [
                        {
                            "id": nint(row["nbpers_id"]),
                            "type":"nbpers",
                            "duration":0,
                            "breadcrumb": "1 personne"
                        },{
                            "id": nint(row["majeurs_id"]),
                            "type":"radio",
                            "duration":0,
                            "breadcrumb": "Il n\'y a que des personnes majeures"
                        },{
                            "id": nint(row["radiocity_id"]),
                            "radiocityId": nint(row["radiocity_id"]),
                            "type":"radiocity",
                            "value":{
                                "city":city_name,
                                "zip_code": city_postal
                            },
                            "breadcrumb": city_name
                        }, {
                            "id": nint(row["pre_commande_id"]),
                            "value": {"value": precmd_id},
                            "type":"text",
                            "breadcrumb":"Pré-demande"
                        }
                    ]
            }

            response = requests.post('https://ws.synbird.com/v6/pro/company/getSlotsFor', headers=headers, data=json.dumps(data))
            response_data = response.json()
            
            for place in response_data["timeSlots"]:
                d = datetime.datetime.strptime(place["start_date"], "%Y-%m-%dT%H:%M:%S%z")
                dates.append(d)
                print(datetime.datetime.strftime(d, "%d/%m/%Y"))
                if d.date() < datetime.date(2022, 7, 1):
                    print("^^^ FOUND DATE")
    
    print("---- Meilleure date trouvée ----")
    best = dates[0] if dates else None
    for d in dates:
        if d < best:
            best = d
    best_str = datetime.datetime.strftime(best, "%d/%m/%Y")
    print(best_str)
    with open("data.json", "r+") as f:
        jsond = json.load(f)
    last_best = jsond["best"]
    if last_best != best_str:
        jsond["best"] = best_str
        with open("data.json", "w") as f:
            json.dump(jsond, f)
        bot.send_message(telegram_user_id, "---- Nouvelle meilleure date trouvée ----\n" + best_str)

async def main():
    await send_requests()

if __name__ == '__main__':
    bot = Bot(token=os.environ['TELEGRAM_TOKEN'])
    asyncio.run(main())