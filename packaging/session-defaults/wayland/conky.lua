-- Keep the selected Daylight profile and its resolved network interface.
dofile(assert(os.getenv("DAYLIGHT_CONKY_CONFIG")))
-- Xwayland exposes the desktop as a rootless display. Let Conky size its
-- overlay directly, including when Connect changes the virtual resolution.
conky.config.own_window_type = 'override'
