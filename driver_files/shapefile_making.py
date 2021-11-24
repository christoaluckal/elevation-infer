import geopandas as gpd
from shapely.geometry import Polygon
def make_multiple_shapefile(coords,heights,location,output_name):
    lat_list = []
    lon_list = []
    for shapes in coords:
        lat_list.append(shapes[0][1])
        lon_list.append(shapes[0][0])
    polygon_geom = Polygon(zip(lon_list, lat_list))
    crs = {'init': 'epsg:4326'}
    polygon = gpd.GeoDataFrame(crs=crs, geometry=[polygon_geom])
    polygon['height'] = heights
    polygon.to_file(filename=location+output_name.format(output_name), driver="ESRI Shapefile")
    print("Done")
    return

def make_single_shapefile(coords,heights,location,output):
    full_polys = []
    for building in range(0,len(coords)):
        lat_list = []
        lon_list = []
        for shapes in coords[building]:
            lat_list.append(shapes[0][1])
            lon_list.append(shapes[0][0])


        polygon_geom = Polygon(zip(lon_list, lat_list))
        full_polys.append(polygon_geom)

    crs = {'init': 'epsg:4326'}
    polygon = gpd.GeoDataFrame(crs=crs, geometry=full_polys)
    polygon.insert(1,'height',0.0)
    polygon['height'] = heights
    polygon.to_file(filename=location+output, driver="ESRI Shapefile")