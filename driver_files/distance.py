from shapely.geometry import Polygon, Point
from shapely.ops import nearest_points
from shapely.wkt import loads
import math

# https://gis.stackexchange.com/a/346064
def haversine(coord1, coord2):
    # Coordinates in decimal degrees (e.g. 2.89078, 12.79797)
    lon1, lat1 = coord1
    lon2, lat2 = coord2
    R = 6371000  # radius of Earth in meters
    phi_1 = math.radians(lat1)
    phi_2 = math.radians(lat2)

    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi_1) * math.cos(phi_2) * math.sin(delta_lambda / 2.0) ** 2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    meters = R * c  # output distance in meters

    return meters



def compute_RMSE(coords_list):
    small_poly = Polygon([(74.1512246,15.1079579), (74.1513083,15.1079508), (74.1512989,15.1078027), (74.1512827,15.1077980),(74.1512128,15.1078061)])
    big_poly = Polygon([(74.14924678,15.10868066),(74.14930113,15.10866789),(74.14929959,15.10866169),(74.14934309,15.10865182),(74.14934491,15.10865800),(74.14940730,15.10864375),(74.14940883,15.10864873),(74.14970756,15.10858059),(74.14970574,15.10857442),(74.14972777,15.10856846),(74.14970160,15.10846928),(74.14967823,15.10846897),(74.14938579,15.10853645),(74.14938651,15.10853798),(74.14936413,15.10854393),(74.14936314,15.10854094),(74.14921664,15.10857660),(74.14921878,15.10858733),(74.14920867,15.10859049),(74.14923075,15.10867184),(74.14924137,15.10866868),(74.14924678,15.10868066)])
    grain_poly = Polygon([(74.14902220,15.10697961),(74.14903977,15.10698299),(74.14930503,15.10685196),(74.14931055,15.10682964),(74.14920626,15.10663995),(74.14918415,15.10663422),(74.14892192,15.10677296),(74.14891620,15.10679024)])
    cluster_poly = Polygon([(74.1506579,15.1082795),(74.1507130,15.1082830),(74.1507669,15.1082837),(74.1507840,15.1080178),(74.1507318,15.1080098),(74.1506729,15.1080107)])
    for building in range(0,len(coords_list)):
        rmse_sum = 0
        me_sum = 0
        count = 0
        for shapes in coords_list[building]:
            point = Point(shapes[0][0],shapes[0][1])
            p1 = loads(cluster_poly.exterior.interpolate(cluster_poly.exterior.project(point)).wkt)
            # print(type(p1))
            dist=haversine((point.x,point.y),(p1.x,p1.y))
            rmse_sum+=dist**2
            me_sum+=dist
            count+=1

        rmse_sum = rmse_sum/count
        rmse_sum = math.sqrt(rmse_sum)
        print("RMSE:",rmse_sum)

        me_sum = me_sum/count
        print("ME:",me_sum)
        # polygon_geom = Polygon(zip(lon_list, lat_list))


# small_poly = Polygon([(74.1512246,15.1079579), (74.1513083,15.1079508), (74.1512989,15.1078027), (74.1512827,15.1077980),(74.1512128,15.1078061)])
# big_poly = Polygon([(74.14924678,15.10868066),(74.14930113,15.10866789),(74.14929959,15.10866169),(74.14934309,15.10865182),(74.14934491,15.10865800),(74.14940730,15.10864375),(74.14940883,15.10864873),(74.14970756,15.10858059),(74.14970574,15.10857442),(74.14972777,15.10856846),(74.14970160,15.10846928),(74.14967823,15.10846897),(74.14938579,15.10853645),(74.14938651,15.10853798),(74.14936413,15.10854393),(74.14936314,15.10854094),(74.14921664,15.10857660),(74.14921878,15.10858733),(74.14920867,15.10859049),(74.14923075,15.10867184),(74.14924137,15.10866868),(74.14924678,15.10868066)])
# grain_poly = Polygon([(74.14902220,15.10697961),(74.14903977,15.10698299),(74.14930503,15.10685196),(74.14931055,15.10682964),(74.14920626,15.10663995),(74.14918415,15.10663422),(74.14892192,15.10677296),(74.14891620,15.10679024)])
# cluster_poly = Polygon([(74.1506579,15.1082795),(74.1507130,15.1082830),(74.1507669,15.1082837),(74.1507840,15.1080178),(74.1507318,15.1080098),(74.1506729,15.1080107)])
# point = Point(74.14925099,15.10668434)
# # The points are returned in the same order as the input geometries:

# print(grain_poly.distance(point))
# print(grain_poly.boundary.distance(point)*111319.488*math.cos(math.pi*15.10668434/180))
# print(grain_poly.exterior.interpolate(grain_poly.exterior.project(point)).wkt)

# # p1, p2 = nearest_points(point,grain_poly)
# # print(p1.wkt)
# # print(p2.wkt)

# p1, p2 = nearest_points(grain_poly,point)
# print(p1.wkt)
# print(haversine((p1.x,p1.y),(point.x,point.y)))