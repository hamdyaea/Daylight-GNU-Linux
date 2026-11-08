-- Use a native, non-interactive Wayland desktop surface for the full profile.
-- SPDX-License-Identifier: GPL-3.0-only
dofile(assert(os.getenv('DAYLIGHT_CONKY_CONFIG')))
-- Keep the renderer in the appearance owner's process lifecycle.
conky.config.background = false
conky.config.out_to_x = false
conky.config.out_to_wayland = true
