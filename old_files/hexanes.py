import marimo

__generated_with = "0.16.5"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import polars as pl
    import numpy as np
    import seaborn as sns
    import hdmedians as hdm

    import rmsd_map
    from rmsd_map.mol_io.cor_reader import read_cor_file
    from rmsd_map.mol_io.fragment import Fragment
    from rmsd_map.rmsd.pipelines import align_fragments
    return Fragment, align_fragments, hdm, mo, np, pl, read_cor_file, sns


@app.cell
def _(mo):
    mo.md(
        r"""
    To generate UMAP files from `hexanes_rwp5_constr.cor` run

    ``` sh
    > rmsd-map-distances -o hexanes_rwp5_constr hexanes_rwp5_constr.cor
    > rmsd-map-umaps -o hexanes_rwp5_constr_umaps hexanes_rwp5_constr.npz
    > rmsd-map-umaps -d -o hexanes_rwp5_constr_umaps_d hexanes_rwp5_constr.npz
    ```
    """
    )
    return


@app.cell
def _(np, pl, read_cor_file):
    # Reading files

    cor = read_cor_file("./hexanes_rwp5_constr.cor")
    cor = np.asarray(cor, dtype=object)
    um = pl.read_csv("./hexanes_rwp5_constr_umaps.csv") # Vanilla UMAP
    ud = pl.read_csv("./hexanes_rwp5_constr_umaps_d.csv") # Denity-preserving UMAP 
    return cor, ud


@app.cell
def _(hdm, np, pl):
    # stupid central point chooser

    def representative_point_idx(df):
        points = df.select(pl.col("X", "Y")).to_numpy()
        median = hdm.geomedian(points, axis = 0)
        dists = np.linalg.norm(points - median, axis=1)
        return np.argmin(dists)
    return (representative_point_idx,)


@app.cell
def _(pl, sns, ud):
    # Chose umap/distmap and N neighbors

    df = ud.filter(pl.col("N") == 30)
    sns.scatterplot(data = df , x="X", y="Y")
    return (df,)


@app.cell
def _(df, pl, sns):
    # DBSCAN  clustering

    import sklearn.cluster as clu

    dbscan = clu.DBSCAN(eps=0.5, min_samples=5).fit(df.select(pl.col("X", "Y")).to_numpy())
    df2 = df.with_columns(pl.Series("label", dbscan.labels_))
    sns.scatterplot(data = df2 , x="X", y="Y", hue="label", palette="tab10")
    return dbscan, df2


@app.cell
def _(Fragment, cor, df2, mo):
    # Plotting cluster 0 fragments as is

    clu0 = cor[df2["label"] == 0]
    clu0_view_raw = Fragment.plot_fragments(clu0)
    mo.iframe(clu0_view_raw.write_html(fullpage=True),height=400)
    return (clu0,)


@app.cell
def _(Fragment, align_fragments, clu0, df2, mo, pl, representative_point_idx):
    # Now aligned version

    clu0_center_idx = representative_point_idx(df2.filter(pl.col("label") == 0) ) # find a central point on umap
    clu0_aligned = align_fragments(clu0, clu0_center_idx) # and align all fragments to it

    clu0_view = Fragment.plot_fragments(clu0_aligned)
    mo.iframe(clu0_view.write_html(fullpage=True),height=400)
    return (clu0_center_idx,)


@app.cell
def _(Fragment, align_fragments, cor, df2, mo, pl, representative_point_idx):
    # CLuster 1

    clu1 = cor[df2["label"] == 1]
    clu1_center_idx = representative_point_idx(df2.filter(pl.col("label") == 1) )
    clu1_aligned = align_fragments(clu1, clu1_center_idx)

    clu1_view = Fragment.plot_fragments(clu1_aligned)
    mo.iframe(clu1_view.write_html(fullpage=True),height=400)
    return


@app.cell
def _(
    Fragment,
    align_fragments,
    cor,
    dbscan,
    df2,
    mo,
    pl,
    representative_point_idx,
):
    # Cluster 2

    clu2 = cor[dbscan.labels_ == 2]
    clu2_center_idx = representative_point_idx(df2.filter(pl.col("label") == 2) )
    clu2_aligned = align_fragments(clu2, clu2_center_idx)
    clu2_view = Fragment.plot_fragments(clu2_aligned)
    mo.iframe(clu2_view.write_html(fullpage=True),height=400)
    return


@app.cell
def _(
    Fragment,
    align_fragments,
    cor,
    dbscan,
    df2,
    mo,
    pl,
    representative_point_idx,
):
    # Cluster 3

    clu3 = cor[dbscan.labels_ == 3]
    clu3_center_idx = representative_point_idx(df2.filter(pl.col("label") == 3) )

    clu3_aligned = align_fragments(clu3, clu3_center_idx)

    clu3_view = Fragment.plot_fragments(clu3_aligned)
    mo.iframe(clu3_view.write_html(fullpage=True),height=400)
    return (clu3,)


@app.cell
def _(Fragment, align_fragments, clu0, clu0_center_idx, clu3, mo, np):
    # Do clu0 and clu3 represent the same conformer? // styling by model index

    clu03 = np.concatenate([clu0, clu3])
    cl03_aligned = align_fragments(clu03, clu0_center_idx)
    clu03_view = Fragment.plot_fragments(cl03_aligned)
    clu0_idx  = list(range(len(clu0)))
    clu3_idx = list(range(len(clu0), len(clu03)))
    #clu03_view.addStyle({'model': list(range(len(clu0)))}, {'line': {'color': 'green'}})
    clu03_view.addStyle({'model': clu0_idx}, {'line': {'color': 'green'}})
    clu03_view.addStyle({'model': clu3_idx}, {'line': {'color': 'red'}})
    mo.iframe(clu03_view.write_html(fullpage=True),height=400)
    return


if __name__ == "__main__":
    app.run()
