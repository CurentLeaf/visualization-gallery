# Visualization research gallery

One static page with actual ggdist and missingno figures plus interactive Plotly, D3, and Cytoscape.js examples. All reports are synthetic. A small Streamlit companion is included; it does not run on GitHub Pages and is not identical to the complete browser gallery.

## Publishing
The included Actions workflow generates figures and attempts to enable and deploy GitHub Pages. Check the Actions tab after committing. If automatic enablement is denied, select Settings > Pages > Source > GitHub Actions, then rerun the workflow. No live deployment is guaranteed until the workflow succeeds. Repository administrators control Pages settings.

## Local use
Use Python 3.11. Install dependencies with `python -m pip install pandas==2.2.3 matplotlib==3.9.2 missingno==0.5.2 plotly streamlit`. Run `python build.py`. Install R separately and run `install.packages(c("ggplot2","ggdist"))` in R; then run `Rscript uncertainty.R`. Serve the full page with `python -m http.server 8000 --directory site` and visit localhost:8000. Start the companion with `python -m streamlit run app.py`.

## Limits
Browser libraries require CDN access. Provenance is an illustrative chain, not inferred lineage. The summary omits fields intentionally. Intervals represent simulated temperature draws, not calibrated source trust. No sensitive data should be added without a security review. Browser, R, and deployment behavior must be verified on the first workflow run. No global cross-chart selection is implemented.

Sources: https://github.com/ResidentMario/missingno ; https://github.com/mjskay/ggdist ; https://docs.github.com/pages
