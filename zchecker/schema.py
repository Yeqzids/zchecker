# Licensed under a 3-clause BSD style license - see LICENSE.rst
schema = [
    '''CREATE TABLE IF NOT EXISTS nights(
    nightid INTEGER PRIMARY KEY,
    date TEXT UNIQUE,
    nframes INTEGER
    )''',

    '''CREATE TABLE IF NOT EXISTS obs(
    nightid INTEGER,
    infobits INTEGER,
    field INTEGER,
    ccdid INTEGER,
    qid INTEGER,
    rcid INTEGER,
    fid INTEGER,
    filtercode TEXT,
    pid INTEGER PRIMARY KEY,
    expid INTEGER,
    obsdate TEXT,
    obsjd FLOAT,
    filefracday INTEGER,
    seeing FLOAT,
    airmass FLOAT,
    moonillf FLOAT,
    maglimit FLOAT,
    crpix1 FLOAT,
    crpix2 FLOAT,
    crval1 FLOAT,
    crval2 FLOAT,
    cd11 FLOAT,
    cd12 FLOAT,
    cd21 FLOAT,
    cd22 FLOAT,
    ra FLOAT,
    dec FLOAT,
    ra1 FLOAT,
    dec1 FLOAT,
    ra2 FLOAT,
    dec2 FLOAT,
    ra3 FLOAT,
    dec3 FLOAT,
    ra4 FLOAT,
    dec4 FLOAT,
    FOREIGN KEY(nightid) REFERENCES nights(nightid)
    )''',

    '''CREATE TABLE IF NOT EXISTS eph(
    desg TEXT,
    jd FLOAT,
    ra FLOAT,
    dec FLOAT,
    dra FLOAT,
    ddec FLOAT,
    vmag FLOAT,
    retrieved TEXT
    )''',

    'CREATE UNIQUE INDEX IF NOT EXISTS desg_jd ON eph(desg,jd)',

    '''CREATE TABLE IF NOT EXISTS found(
    foundid INTEGER PRIMARY KEY,
    desg TEXT,
    obsjd TEXT,
    ra FLOAT,
    dec FLOAT,
    dra FLOAT,
    ddec FLOAT,
    ra3sig FLOAT,
    dec3sig FLOAT,
    vmag FLOAT,
    rh FLOAT,
    rdot FLOAT,
    delta FLOAT,
    phase FLOAT,
    selong FLOAT,
    sangle FLOAT,
    vangle FLOAT,
    trueanomaly FLOAT,
    tmtp FLOAT,
    pid INTEGER,
    x INTEGER,
    y INTEGER,
    retrieved TEXT,
    archivefile TEXT,
    sci_sync_date TEXT,
    sciimg INTEGER,
    mskimg INTEGER,
    scipsf INTEGER,
    diffimg INTEGER,
    diffpsf INTEGER,
    FOREIGN KEY(pid) REFERENCES obs(pid)
    )''',

    'CREATE UNIQUE INDEX IF NOT EXISTS desg_pid ON found(desg,pid)',

    '''CREATE VIEW IF NOT EXISTS obsnight AS
    SELECT * FROM obs INNER JOIN nights ON obs.nightid=nights.nightid''',

    '''CREATE VIEW IF NOT EXISTS foundobs AS
    SELECT * FROM found
    INNER JOIN obs ON obs.pid=found.pid
    INNER JOIN cutouturl ON found.foundid=cutouturl.foundid''',

    '''CREATE VIEW IF NOT EXISTS cutouturl (foundid,url) AS
    SELECT
      foundid,
      printf("https://irsa.ipac.caltech.edu/ibe/data/ztf/products/sci/%s/%s/%s/ztf_%s_%06d_%s_c%02d_o_q%1d_sciimg.fits?center=%f,%fdeg",
        substr(filefracday,1,4),
        substr(filefracday,5,4),
        substr(filefracday,9),
        filefracday,
        field,
        filtercode,
        ccdid,
        qid,
        found.ra,
        found.dec)
    FROM found INNER JOIN obs ON obs.pid=found.pid''',

    # for zproject
    '''CREATE TABLE IF NOT EXISTS projections(
    foundid INTEGER PRIMARY KEY,
    vangleimg INTEGER,
    sangleimg INTEGER,
    FOREIGN KEY(foundid) REFERENCES found(foundid)
    )''',

    # for zstack
    '''CREATE TABLE IF NOT EXISTS stacks(
    foundid INTEGER PRIMARY KEY,
    stackfile TEXT,
    stacked INTEGER,
    FOREIGN KEY(foundid) REFERENCES found(foundid)
    )''',

    # triggers and file clean up
    '''CREATE TABLE IF NOT EXISTS stale_files(
      path TEXT,
      archivefile TEXT
    )''',

    '''CREATE TRIGGER IF NOT EXISTS delete_found BEFORE DELETE ON found
    BEGIN
      INSERT INTO stale_files
        SELECT 'cutout path',archivefile FROM found
        WHERE foundid=old.foundid
          AND archivefile IS NOT NULL;
      DELETE FROM projections WHERE foundid=old.foundid;
      INSERT INTO stale_files
        SELECT 'stack path',stackfile FROM stacks
        WHERE foundid=old.foundid
          AND stackfile IS NOT NULL;
      DELETE FROM stacks WHERE foundid=old.foundid;
    END;
    ''',

    '''CREATE TRIGGER IF NOT EXISTS delete_obs BEFORE DELETE ON obs
    BEGIN
      DELETE FROM found WHERE pid=old.pid;
    END;
    ''',

    '''CREATE TRIGGER IF NOT EXISTS delete_nights BEFORE DELETE ON nights
    BEGIN
      DELETE FROM obs WHERE nightid=old.nightid;
    END;
    ''',
]
