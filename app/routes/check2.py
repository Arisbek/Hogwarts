from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import json
import numpy as np
import cv2
import base64

check2 = APIRouter()

@check2.post("/check2/{variant}")
async def read_test(
    variant: str,
    frame: str       = Form(...),
    image: UploadFile = File(...)
):
    # 1) Parse frame JSON
    try:
        frame_data = json.loads(frame)
        groups     = frame_data.get("groups", [])
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid frame JSON")

    # 2) Decode uploaded image
    contents = await image.read()
    nparr    = np.frombuffer(contents, np.uint8)
    full_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if full_img is None:
        raise HTTPException(status_code=400, detail="Could not decode image")
    cv2.imshow("main", full_img)
    cv2.waitKey(5000)
    cv2.destroyWindow("main")

    all_crops = []

    # 3) Iterate groups
    for gi, g in enumerate(groups, start=1):
        grp_qnum = g.get("question", f"{gi}")
        squares  = g.get("squares", [])
        grp_crops = []

        # 3a) Optional: crop & show the full group region
        # (Uncomment if you want to debug group-level crop)
        # gx, gy = int(g["x"]), int(g["y"])
        # gw, gh = int(g["width"]), int(g["height"])
        # group_crop = full_img[gy:gy+gh, gx:gx+gw]
        # cv2.imshow(f"Group {grp_qnum}", group_crop)
        # cv2.waitKey(500); cv2.destroyWindow(f"Group {grp_qnum}")

        # 3b) Now crop each square in this group
        for si, sq in enumerate(squares, start=1):
            x = int(sq["x"])
            y = int(sq["y"])
            w = int(sq["width"])
            h = int(sq["height"])

            # bounds check
            if x < 0 or y < 0 or x + w > full_img.shape[1] or y + h > full_img.shape[0]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Square #{si} in group {grp_qnum} out of bounds: {[x,y,w,h]}"
                )

            crop = full_img[y : y + h, x : x + w]

            # show each square (for 1 second)
            win = f"Q{grp_qnum}-S{si}"
            cv2.imshow(win, crop)
            cv2.waitKey(5000)
            cv2.destroyWindow(win)

            # encode and store
            success, buf = cv2.imencode(".png", crop)
            if not success:
                raise HTTPException(status_code=500, detail=f"Failed to encode square #{si} of group {grp_qnum}")
            b64 = base64.b64encode(buf.tobytes()).decode("ascii")

            grp_crops.append({
                "square_index": si,
                "crop_base64": b64
            })

        all_crops.append({
            "question": grp_qnum,
            "squares": grp_crops
        })

    # 4) Return JSON with all the square crops
    return JSONResponse({
        "variant": variant,
        "groups": all_crops
    })
