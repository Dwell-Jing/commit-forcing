"""Shared restrained colors for active manuscript figures.

Measured series use ink/clay and retain distinct markers/line styles.
Diagram context roles use gray/blue/clay. Status badges alone use red/green;
source illustrations and experimental image pixels are never recolored.
"""

INK = '#202B33'
MUTED = '#67717A'
RULE = '#D8DDE0'
BLUE = '#527F9D'
BLUE_LIGHT = '#D7E7F2'
# Match the LovartAccent value in lovartreport.cls.
ACCENT = '#A64F35'
ACCENT_LIGHT = '#F2DCCE'
NONRECENT = MUTED
NONRECENT_LIGHT = '#E8EBED'
POSITIVE = '#237C51'
NEGATIVE = '#C93428'
PLOT_PRIMARY = INK
PLOT_SECONDARY = ACCENT
PLOT_CONTROL = MUTED

# Diagram fills match the Figure 1 tensor and committing representations.
TENSOR_FILL = '#FAFBFC'
LATENT_FILL = '#EDF3F6'
COMMIT_FILL = '#FCF9F6'
WINDOW_CURRENT_FILL = '#F7EEE9'
GRID_RULE = '#BEC8CE'
