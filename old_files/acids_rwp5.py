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
    from rmsd_map.rmsd.pipelines import align_fragments, chain_fragments_naive, chain_fragments, partial_align_fragments

    from vis import ChooseLineWidget, sort_along
    return (
        ChooseLineWidget,
        Fragment,
        align_fragments,
        chain_fragments,
        hdm,
        mo,
        np,
        partial_align_fragments,
        pl,
        read_cor_file,
        sns,
        sort_along,
    )


@app.cell
def _(np, pl, read_cor_file):
    # Reading files

    cor = read_cor_file("./acids_rwp5_all_noh.cor")
    cor = np.asarray(cor, dtype=object)
    um = pl.read_csv("./acids_rwp5_all_noh_umaps.csv") # Vanilla UMAP
    ud = pl.read_csv("./acids_rwp5_all_noh_umaps_d.csv") # Denity-preserving UMAP with UMAP(densmap=True)
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

    df = ud.filter(pl.col("N") == 40)
    sns.scatterplot(data = df , x="X", y="Y")
    return (df,)


@app.cell
def _(df, pl, sns):
    # DBSCAN  clustering

    import sklearn.cluster as clu

    dbscan = clu.DBSCAN(eps=0.4, min_samples=5).fit(df.select(pl.col("X", "Y")).to_numpy())
    df2 = df.with_columns(pl.Series("label", dbscan.labels_))
    sns.scatterplot(data = df2 , x="X", y="Y", hue="label", palette="tab10")
    return (df2,)


@app.cell
def _(Fragment, align_fragments, cor, df2, mo, pl, representative_point_idx):
    # CLuster 1

    clu1 = cor[df2["label"] == 2]
    clu1_center_idx = representative_point_idx(df2.filter(pl.col("label") == 1) )
    clu1_aligned = align_fragments(clu1, clu1_center_idx)

    clu1_view = Fragment.plot_fragments(clu1_aligned)
    mo.iframe(clu1_view.write_html(fullpage=True),height=400)
    return clu1_aligned, clu1_center_idx


@app.cell
def _(
    Fragment,
    clu1_aligned,
    clu1_center_idx,
    mo,
    np,
    partial_align_fragments,
):
    #Partial after align

    clu1_partial_aligned = partial_align_fragments(clu1_aligned, np.arange(4) , n_center = clu1_center_idx)
    clu1_partial_view = Fragment.plot_fragments(clu1_partial_aligned)
    mo.iframe(clu1_partial_view.write_html(fullpage=True),height=400)
    return


@app.cell
def _(ChooseLineWidget, df2, pl):
    clu1_df = df2.filter(pl.col("label") == 2)

    w1 = ChooseLineWidget(clu1_df, "X", "Y")
    w1.line_points = [{'x': -1.847634342211537, 'y': 1.6674842588352272}, {'x': -1.9971312964423074, 'y': 1.9194439982291667}, {'x': -2.1715444097115393, 'y': 2.221795685501894}, {'x': -2.2878198185576926, 'y': 2.3855695161079544}, {'x': -2.487149090865384, 'y': 2.473755424895834}, {'x': -2.8276699310576925, 'y': 2.5619413336837127}, {'x': -3.0768315214423083, 'y': 2.473755424895834}, {'x': -3.2844661800961537, 'y': 2.2721876333806814}, {'x': -3.5170169977884616, 'y': 2.1714037376231063}, {'x': -3.6748193383653844, 'y': 2.1336097767140147}, {'x': -3.8741486106730765, 'y': 2.0454238679261363}, {'x': -4.03195095125, 'y': 2.1084138027746215}, {'x': -4.24789099625, 'y': 1.995031920047348}, {'x': -4.330944859711538, 'y': 1.7934641285321966}, {'x': -4.5219687456730755, 'y': 1.6422882848958333}, {'x': -4.870794972211538, 'y': 1.4407204933806816}, {'x': -5.194705039711538, 'y': 1.5415043891382578}, {'x': -5.277758903173077, 'y': 1.5792983500473483}, {'x': -5.659806675096154, 'y': 1.2517506888352274}, {'x': -5.60997435701923, 'y': 1.0501828973200755}, {'x': -5.535225879903845, 'y': 0.8738110797443187}, {'x': -5.43556124375, 'y': 0.6470473142897736}, {'x': -5.369118152980769, 'y': 0.4580775097443186}, {'x': -4.82926804048077, 'y': 0.48327348368371237}, {'x': -4.712992631634615, 'y': 0.29430367913825806}, {'x': -4.455525654903846, 'y': 0.2439117312594702}, {'x': -4.3475556324038465, 'y': -0.033243982073863476}, {'x': -3.9987294058653844, 'y': -0.0962339169223484}, {'x': -4.148226360096153, 'y': -0.17182183874053014}, {'x': -4.231280223557691, 'y': -0.360791643285985}, {'x': -4.297723314326923, 'y': -0.4237815781344698}, {'x': -4.222974837211538, 'y': -0.5497614478314395}, {'x': -3.899064769711538, 'y': -0.9151030699526514}, {'x': -3.8658432243269227, 'y': -1.116670861467803}, {'x': -3.81601090625, 'y': -1.3056406660132578}, {'x': -3.807705519903846, 'y': -1.444218522679925}, {'x': -3.467184679711538, 'y': -1.0536809266193181}, {'x': -3.2263284756730766, 'y': -0.7513292393465905}, {'x': -3.101747680480769, 'y': -0.6505453435890154}, {'x': -2.860891476442307, 'y': -0.5245654738920454}, {'x': -2.6864783631730766, 'y': -0.360791643285985}, {'x': -2.5785083406730767, 'y': -0.05843995601325758}, {'x': -2.3625682956730767, 'y': 0.33209764004734876}, {'x': -2.229682114134615, 'y': 0.4202835488352272}, {'x': -1.8227181831730768, 'y': 0.47067549671401576}, {'x': -1.7396643197115367, 'y': 0.8738110797443187}, {'x': -1.4905027293269233, 'y': 1.0123889364109853}, {'x': -1.3991434795192308, 'y': 1.0123889364109848}]



    w1
    return clu1_df, w1


@app.cell
def _(Fragment, chain_fragments, clu1_aligned, clu1_df, mo, sort_along, w1):
    print(w1.line_points)
    clu1_idx = sort_along(w1.line_points, clu1_df, 0.1)

    clu1_sorted = clu1_aligned[clu1_idx]

    clu1_chain = chain_fragments(clu1_sorted)

    clu1_chain_view = Fragment.plot_fragments(clu1_chain)
    mo.iframe(clu1_chain_view.write_html(fullpage=True),height=400)
    return (clu1_chain,)


@app.cell
def _(Fragment, clu1_chain, mo, np, partial_align_fragments, sns):
    #Partial after chain

    clu1_partial_chained = partial_align_fragments(clu1_chain, np.arange(4,8) , 30)
    clu1_partial_chained_view = Fragment.plot_fragments(clu1_partial_chained)

    _aa = sns.color_palette("viridis", len(clu1_partial_chained)).as_hex()

    for _i, _ in enumerate(clu1_partial_chained):
            clu1_partial_chained_view.addStyle({'model': _i}, {'line': {'color': _aa[_i]}})

    mo.iframe(clu1_partial_chained_view.write_html(fullpage=True),height=400)
    return


@app.cell
def _(Fragment, align_fragments, cor, df2, mo, pl, representative_point_idx):
    # CLuster 3

    clu3 = cor[df2["label"] == 3]
    clu3_center_idx = representative_point_idx(df2.filter(pl.col("label") == 3) )
    clu3_aligned = align_fragments(clu3, clu3_center_idx)

    clu3_view = Fragment.plot_fragments(clu3_aligned)
    mo.iframe(clu3_view.write_html(fullpage=True),height=400)
    return clu3_aligned, clu3_center_idx


@app.cell
def _(
    Fragment,
    clu3_aligned,
    clu3_center_idx,
    mo,
    np,
    partial_align_fragments,
):
    #Partial after align

    clu3_partial_aligned = partial_align_fragments(clu3_aligned, np.arange(4) , n_center = clu3_center_idx)
    clu3_partial_view = Fragment.plot_fragments(clu3_partial_aligned)
    mo.iframe(clu3_partial_view.write_html(fullpage=True),height=400)
    return


@app.cell
def _(ChooseLineWidget, df2, pl):
    clu3_df = df2.filter(pl.col("label") == 3)

    w3 = ChooseLineWidget(clu3_df, "X", "Y")
    w3.line_points = [{'x': -3.4665110125, 'y': 3.9295742605303037}, {'x': -3.7725554009615387, 'y': 3.746462030227273}, {'x': -4.107746874038463, 'y': 3.4717936847727273}, {'x': -4.362783864423077, 'y': 3.554194188409091}, {'x': -4.661541481730769, 'y': 3.892951814469697}, {'x': -5.2080493182692305, 'y': 3.7098395841666667}, {'x': -5.579674647115385, 'y': 4.03028598719697}, {'x': -5.521380477884616, 'y': 4.469755339924243}, {'x': -5.79827778173077, 'y': 4.369043613257576}, {'x': -6.089748627884616, 'y': 4.442288505378788}, {'x': -6.337498847115385, 'y': 4.588778289621212}, {'x': -6.9714479375, 'y': 4.76273490840909}, {'x': -7.1098965894230775, 'y': 4.726112462348485}, {'x': -6.898580225961537, 'y': 4.927535915681819}, {'x': -6.818425743269231, 'y': 5.211359872651515}, {'x': -6.607109379807693, 'y': 5.348694045378789}, {'x': -6.337498847115385, 'y': 5.687451671439394}, {'x': -6.09703539903846, 'y': 5.898030736287879}, {'x': -5.878432264423077, 'y': 5.898030736287879}, {'x': -5.484946622115386, 'y': 5.934653182348485}, {'x': -5.317350885576923, 'y': 5.632518002348485}, {'x': -5.033166810576923, 'y': 5.312071599318182}]



    w3
    return clu3_df, w3


@app.cell
def _(
    Fragment,
    chain_fragments,
    clu3_aligned,
    clu3_df,
    mo,
    np,
    partial_align_fragments,
    sns,
    sort_along,
    w3,
):
    print(w3.line_points)
    clu3_idx = sort_along(w3.line_points, clu3_df, 0.1)
    clu3_sorted = clu3_aligned[clu3_idx]
    clu3_chain = chain_fragments(clu3_sorted)

    clu3_partial_chained = partial_align_fragments(clu3_chain, np.arange(4) , 30)
    clu3_partial_chained_view = Fragment.plot_fragments(clu3_partial_chained)

    _aa = sns.color_palette("viridis", len(clu3_partial_chained)).as_hex()

    for _i, _ in enumerate(clu3_partial_chained):
            clu3_partial_chained_view.addStyle({'model': _i}, {'stick': {'color': _aa[_i]}})

    mo.iframe(clu3_partial_chained_view.write_html(fullpage=True),height=400)
    return


if __name__ == "__main__":
    app.run()
