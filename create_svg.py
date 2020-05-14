from shapely.geometry.multipolygon import MultiPolygon
import geopandas as gpd
import pandas as pd
import svgwrite
import os


def poly_path(poly):
    exterior_coords = [
        ["{},{}".format(*c) for c in poly.exterior.coords]]
    interior_coords = [
        ["{},{}".format(*c) for c in interior.coords]
        for interior in poly.interiors]
    path = " ".join([
        "M {} L {} z".format(coords[0], " L ".join(coords[1:]))
        for coords in exterior_coords + interior_coords])
    return path


def get_path(shape):
    if isinstance(shape, MultiPolygon):
        return ' '.join([poly_path(poly) for poly in shape])
    return poly_path(shape)


def create_svg_of_state(state_gdf, state):
    os.makedirs('output', exist_ok=True)
    gdf = state_gdf.to_crs(epsg=state['crs']).copy()
    x1, y1, x2, y2 = gdf.total_bounds
    factor = 400/(max(abs(x1-x2), abs(y1-y2)))
    gdf['geometry'] = gdf.geometry.translate(-x1, -y2).scale(factor, -factor, origin=(0, 0))
    dwg = svgwrite.Drawing('output/{}_{}.svg'.format(state['fips'], state['name']), height='400')
    dwg.fill(color='#d0d0d0')
    dwg.stroke(color='#ffffff', width=1)
    g = svgwrite.container.Group(id='counties')
    for i, row in gdf.iterrows():
        path = svgwrite.path.Path(d=get_path(row.geometry), id='c{}'.format(row['GEOID']))
        g.add(path)
    dwg.add(g)
    dwg.save()


if __name__ == '__main__':
    states_gdf = gpd.read_file('https://www2.census.gov/geo/tiger/GENZ2019/shp/cb_2019_us_county_20m.zip')
    states = pd.read_csv('states.csv', dtype=str)
    states.index = states.fips
    for statefp in states_gdf.STATEFP.unique():
        create_svg_of_state(states_gdf[states_gdf.STATEFP == statefp], states.loc[statefp])
