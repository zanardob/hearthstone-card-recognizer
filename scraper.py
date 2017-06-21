from bs4 import BeautifulSoup
import urllib.request


def gather(filter, pages):
    images = []
    for page in range(1, pages):
        url = "http://www.hearthpwn.com/cards?filter-type=" \
              + str(filter) + "&page=" + str(page)
        html = urllib.request.urlopen(url)
        soup = BeautifulSoup(html, "html.parser")
        images += soup.findAll("img")

    return images


def main():
    images = []

    # Gather minions
    print("Gathering minions...")
    images += gather(5, 7)

    # Gather spells
    print("Gathering spells...")
    images += gather(4, 13)

    # Gather weapons
    print("Gathering weapons...")
    images += gather(7, 7)

    # Download the images
    print("Fetching the images...")
    total = len(images)
    for i in range(total):
        name = images[i]["data-href"].split("/")[2]
        path = "db/" + name + ".png"
        src = images[i]["src"]

        message = "(" + str(i+1) + "/" + str(total) + ") "

        try:
            urllib.request.urlretrieve(src, path)
            print(message + name)
        except:
            print(message + "Card " + name + " couldn't be fetched.")
            continue

    print("All done!")


if __name__ == '__main__':
    main()
