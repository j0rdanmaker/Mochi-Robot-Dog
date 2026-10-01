# RobotDog wiring diagrams - render all WireViz sources.
#
# Usage (from anywhere; also works as `make -C hardware/wiring ...`):
#   make          - render every source/*.yml that changed since its last render
#   make clean    - remove all generated output
#
# Sources live in source/, rendered output goes to output/. We render HTML,
# SVG, and TSV only (-f hst); SVG is sharp at any zoom and diffable, so PNG is
# skipped - see README.md.

SRC_DIR := source
OUT_DIR := output

YML_FILES := $(wildcard $(SRC_DIR)/*.yml)
SVG_FILES := $(patsubst $(SRC_DIR)/%.yml,$(OUT_DIR)/%.svg,$(YML_FILES))

.PHONY: all clean

all: $(SVG_FILES)

# Rendering one .yml produces .html/.svg/.tsv together; the .svg is used
# here as the make target that stands in for "this diagram is up to date".
$(OUT_DIR)/%.svg: $(SRC_DIR)/%.yml | $(OUT_DIR)
	uv run wireviz -f hst -o $(OUT_DIR) $<

$(OUT_DIR):
	mkdir -p $@

clean:
	rm -f $(OUT_DIR)/*.svg $(OUT_DIR)/*.png $(OUT_DIR)/*.html $(OUT_DIR)/*.tsv $(OUT_DIR)/*.gv
