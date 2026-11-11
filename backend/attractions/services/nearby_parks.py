from functools import lru_cache

import numpy as np
import shapely
from pyproj import Transformer
from shapely import STRtree, box
from shapely.geometry import Point

from attractions.models import NationalPark

# Albers equal-area for the US/Canada. Distances are approximate (~1-2%),
# which is fine for a 25-mile corridor.
_transformer = Transformer.from_crs(4326, 5070, always_xy=True)
METERS_PER_MILE = 1609.344

PARK_SIMPLIFY_DEG = 0.005    # ~500 m, applied once at load time
ROUTE_SIMPLIFY_DEG = 0.02    # ~2 km, applied before projecting


def _project(geom):
    """Vectorised reprojection (much faster than shapely.ops.transform)."""
    def fn(coords):
        x, y = _transformer.transform(coords[:, 0], coords[:, 1])
        return np.column_stack((x, y))
    return shapely.transform(geom, fn)


@lru_cache(maxsize=1)
def _load_parks():
    meta, geoms = [], []
    for p in NationalPark.objects.all().iterator():
        if p.polygon:
            simple = p.polygon.simplify(PARK_SIMPLIFY_DEG, preserve_topology=True)
            g = shapely.from_wkb(bytes(simple.wkb))
            approx = False
        else:
            g = Point(p.location.x, p.location.y)
            approx = True
        geoms.append(_project(g))
        meta.append({
            "id": p.id, "name": p.name, "code": p.code, "state": p.state,
            "lat": p.location.y, "lon": p.location.x,
            "distance_is_approximate": approx,
        })
    return meta, geoms, STRtree(geoms)


def find_nearby_parks(route_path, radius_miles=25):
    radius_m = radius_miles * METERS_PER_MILE
    meta, geoms, tree = _load_parks()

    # Simplify in lon/lat with GEOS (fast, C-level) BEFORE projecting.
    simple = route_path.simplify(ROUTE_SIMPLIFY_DEG, preserve_topology=False)
    route = _project(shapely.from_wkb(bytes(simple.wkb)))

    idx = tree.query(route, predicate="dwithin", distance=radius_m)

    results = []
    for i in idx:
        g = geoms[i]
        # Measure against only the stretch of route near this park,
        # not the whole continent-spanning line.
        minx, miny, maxx, maxy = g.bounds
        local = route.intersection(
            box(minx - radius_m, miny - radius_m, maxx + radius_m, maxy + radius_m)
        )
        d = g.distance(local) / METERS_PER_MILE
        results.append({**meta[i], "distance_miles": round(d, 1)})

    results.sort(key=lambda r: r["distance_miles"])
    return results