# PPE Test Images

These images are copied from the local YOLO dataset for quick camera testing.
Each image has exactly one labeled person.

Show one image on a phone/laptop screen, point the Raspberry Pi camera at it, and check the lab output.

Expected cases:

```text
full_helmet_vest_1.jpg..3.jpg     -> helmet OK, vest OK
missing_helmet_1.jpg..3.jpg       -> helmet missing, vest OK
missing_vest_1.jpg..3.jpg         -> helmet OK, vest missing
missing_helmet_vest_1.jpg..3.jpg  -> helmet missing, vest missing
```

These are only for rough testing. Real camera angle, screen glare, and image size can affect detection.
