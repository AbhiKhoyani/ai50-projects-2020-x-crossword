import degrees as dg

dg.load_data("large")
dg.names
dg.people
dg.movies

#n = dg.neighbors_for_person('102')

source= '102'
target = '1597'
path = dg.shortest_path(source, target)
if path is None:
    print("Not connected.")
else:
    print(path)
    degrees = len(path)
    print(f"{degrees} degrees of separation.")
    path = [(None, source)] + path
    for i in range(degrees):
        person1 = dg.people[path[i][1]]["name"]
        person2 = dg.people[path[i + 1][1]]["name"]
        movie = dg.movies[path[i + 1][0]]["title"]
        print(f"{i + 1}: {person1} and {person2} starred in {movie}")


#dg.main()
