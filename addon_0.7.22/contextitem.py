import sys
import xbmcgui
from default import MEDIA, NAME, run

try:
    tag = sys.listitem.getVideoInfoTag()
    itemid = tag.getDbId()
    kind = tag.getMediaType()
    if kind not in MEDIA or itemid < 0:
        raise ValueError('Select a library movie, episode, or music video.')
except Exception as exc:
    xbmcgui.Dialog().ok(NAME, str(exc))
else:
    run(itemid, kind)
