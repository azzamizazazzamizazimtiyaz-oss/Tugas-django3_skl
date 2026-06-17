from types import SimpleNamespace

from django.db import connection, transaction
from django.http import Http404
from django.shortcuts import redirect, render


# ─── HELPER ────────────────────────────────────────────────

def fetch_one(query, params=()):
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        row = cursor.fetchone()
        if row is None:
            return None
        columns = [col[0] for col in cursor.description]
        return SimpleNamespace(**dict(zip(columns, row)))


def fetch_all(query, params=()):
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        return [SimpleNamespace(**dict(zip(columns, row))) for row in cursor.fetchall()]


def execute_query(query, params=()):
    with connection.cursor() as cursor:
        cursor.execute(query, params)


def get_object_or_none(table, pk):
    query = f"SELECT * FROM {table} WHERE id = %s"
    return fetch_one(query, [pk])


def get_count(table, where=None, params=()):
    if where:
        query = f"SELECT COUNT(*) AS total FROM {table} WHERE {where}"
    else:
        query = f"SELECT COUNT(*) AS total FROM {table}"
    result = fetch_one(query, params)
    return result.total if result else 0


# ─── BUKU VIEWS ────────────────────────────────────────────────

def dashboard(request):
    total_buku = get_count('buku_buku')
    total_siswa = get_count('buku_siswa')
    total_peminjaman = get_count('buku_peminjaman')
    peminjaman_aktif = get_count(
        'buku_peminjaman',
        where="status = %s",
        params=('Dipinjam',),
    )
    return render(request, 'perpustakaan/dashboard.html', {
        'total_buku': total_buku,
        'total_siswa': total_siswa,
        'total_peminjaman': total_peminjaman,
        'peminjaman_aktif': peminjaman_aktif,
    })


def buku_list(request):
    buku_list = fetch_all(
        """
        SELECT id, judul, pengarang, kategori, penerbit, tahun_terbit, rak, stok, deskripsi
        FROM buku_buku
        ORDER BY id
        """
    )
    return render(request, 'buku/list.html', {'buku_list': buku_list})


def buku_tambah(request):
    if request.method == 'POST':
        execute_query(
            """
            INSERT INTO buku_buku (
                judul, pengarang, kategori, penerbit, tahun_terbit, rak, stok, deskripsi
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            [
                request.POST['judul'],
                request.POST['pengarang'],
                request.POST['kategori'],
                request.POST['penerbit'],
                request.POST['tahun_terbit'],
                request.POST['rak'],
                request.POST['stok'],
                request.POST.get('deskripsi', ''),
            ],
        )
        return redirect('buku_list')
    return render(request, 'buku/tambah.html')


def buku_detail(request, pk):
    buku = get_object_or_none('buku_buku', pk)
    if buku is None:
        raise Http404
    return render(request, 'buku/detail.html', {'buku': buku})


def buku_edit(request, pk):
    buku = get_object_or_none('buku_buku', pk)
    if buku is None:
        raise Http404
    if request.method == 'POST':
        execute_query(
            """
            UPDATE buku_buku
            SET judul = %s,
                pengarang = %s,
                kategori = %s,
                penerbit = %s,
                tahun_terbit = %s,
                rak = %s,
                stok = %s,
                deskripsi = %s
            WHERE id = %s
            """,
            [
                request.POST['judul'],
                request.POST['pengarang'],
                request.POST['kategori'],
                request.POST['penerbit'],
                request.POST['tahun_terbit'],
                request.POST['rak'],
                request.POST['stok'],
                request.POST.get('deskripsi', ''),
                pk,
            ],
        )
        return redirect('buku_list')
    return render(request, 'buku/edit.html', {'buku': buku})


def buku_delete(request, pk):
    buku = get_object_or_none('buku_buku', pk)
    if buku is None:
        raise Http404
    if request.method == 'POST':
        execute_query('DELETE FROM buku_buku WHERE id = %s', [pk])
        return redirect('buku_list')
    return render(request, 'buku/delete.html', {'buku': buku})


# ─── SISWA VIEWS ───────────────────────────────────────────────

def siswa_list(request):
    siswa_list = fetch_all(
        """
        SELECT id, nama, kelas, nis, is_active
        FROM buku_siswa
        ORDER BY id
        """
    )
    return render(request, 'siswa/list-siswa.html', {'siswa_list': siswa_list})


def siswa_tambah(request):
    if request.method == 'POST':
        is_active = request.POST.get('is_active', 'true') == 'true'
        execute_query(
            """
            INSERT INTO buku_siswa (nama, kelas, nis, is_active)
            VALUES (%s, %s, %s, %s)
            """,
            [request.POST['nama'], request.POST['kelas'], request.POST['nis'], is_active],
        )
        return redirect('siswa_list')
    return render(request, 'siswa/tambah-siswa.html')


def siswa_detail(request, pk):
    siswa = get_object_or_none('buku_siswa', pk)
    if siswa is None:
        raise Http404
    total_peminjaman = get_count(
        'buku_peminjaman',
        where='siswa_id = %s',
        params=(pk,),
    )
    peminjaman_aktif_count = get_count(
        'buku_peminjaman',
        where='siswa_id = %s AND status = %s',
        params=(pk, 'Dipinjam'),
    )
    return render(request, 'siswa/detail-siswa.html', {
        'siswa': siswa,
        'total_peminjaman': total_peminjaman,
        'peminjaman_aktif_count': peminjaman_aktif_count,
    })


def siswa_edit(request, pk):
    siswa = get_object_or_none('buku_siswa', pk)
    if siswa is None:
        raise Http404
    if request.method == 'POST':
        execute_query(
            """
            UPDATE buku_siswa
            SET nama = %s,
                kelas = %s,
                nis = %s,
                is_active = %s
            WHERE id = %s
            """,
            [request.POST['nama'], request.POST['kelas'], request.POST['nis'], request.POST.get('is_active', 'true') == 'true', pk],
        )
        return redirect('siswa_list')
    return render(request, 'siswa/edit-siswa.html', {'siswa': siswa})


def siswa_hapus(request, pk):
    siswa = get_object_or_none('buku_siswa', pk)
    if siswa is None:
        raise Http404
    if request.method == 'POST':
        execute_query('DELETE FROM buku_siswa WHERE id = %s', [pk])
        return redirect('siswa_list')
    return render(request, 'siswa/hapus-siswa.html', {'siswa': siswa})


# ─── PEMINJAMAN VIEWS ─────────────────────────────────────────

def peminjaman_list(request):
    query = """
        SELECT
            p.id,
            p.siswa_id,
            p.buku_id,
            p.tanggal_pinjam,
            p.jatuh_tempo,
            p.keperluan,
            p.catatan,
            p.status,
            s.id AS siswa_model_id,
            s.nama AS siswa_nama,
            s.kelas AS siswa_kelas,
            s.nis AS siswa_nis,
            s.is_active AS siswa_is_active,
            b.id AS buku_model_id,
            b.judul AS buku_judul,
            b.pengarang AS buku_pengarang,
            b.kategori AS buku_kategori,
            b.penerbit AS buku_penerbit,
            b.tahun_terbit AS buku_tahun_terbit,
            b.rak AS buku_rak,
            b.stok AS buku_stok,
            b.deskripsi AS buku_deskripsi
        FROM buku_peminjaman p
        INNER JOIN buku_siswa s ON p.siswa_id = s.id
        INNER JOIN buku_buku b ON p.buku_id = b.id
        ORDER BY p.id
    """

    results = []
    with connection.cursor() as cursor:
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        for row in cursor.fetchall():
            data = dict(zip(columns, row))
            peminjaman = SimpleNamespace(**data)
            peminjaman.siswa = SimpleNamespace(
                id=data['siswa_model_id'],
                nama=data['siswa_nama'],
                kelas=data['siswa_kelas'],
                nis=data['siswa_nis'],
                is_active=data['siswa_is_active'],
            )
            peminjaman.buku = SimpleNamespace(
                id=data['buku_model_id'],
                judul=data['buku_judul'],
                pengarang=data['buku_pengarang'],
                kategori=data['buku_kategori'],
                penerbit=data['buku_penerbit'],
                tahun_terbit=data['buku_tahun_terbit'],
                rak=data['buku_rak'],
                stok=data['buku_stok'],
                deskripsi=data['buku_deskripsi'],
            )
            results.append(peminjaman)

    return render(request, 'peminjaman/list-peminjaman.html', {
        'peminjaman_list': results,
    })


def peminjaman_tambah(request):
    if request.method == 'POST':
        siswa_id = request.POST['siswa_id']
        buku_id = request.POST['buku_id']

        siswa = get_object_or_none('buku_siswa', siswa_id)
        buku = get_object_or_none('buku_buku', buku_id)
        if siswa is None or buku is None:
            raise Http404

        with transaction.atomic():
            if buku.stok > 0:
                execute_query(
                    'UPDATE buku_buku SET stok = stok - 1 WHERE id = %s',
                    [buku_id],
                )
            else:
                return redirect('peminjaman_tambah')

            execute_query(
                """
                INSERT INTO buku_peminjaman (
                    siswa_id, buku_id, tanggal_pinjam, jatuh_tempo,
                    keperluan, catatan, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                [
                    siswa_id,
                    buku_id,
                    request.POST['tanggal_pinjam'],
                    request.POST['jatuh_tempo'],
                    request.POST.get('keperluan', ''),
                    request.POST.get('catatan', ''),
                    'Dipinjam',
                ],
            )
        return redirect('peminjaman_list')

    siswa_list = fetch_all(
        """
        SELECT id, nama, kelas, nis, is_active
        FROM buku_siswa
        WHERE is_active = TRUE
        ORDER BY id
        """
    )
    buku_list = fetch_all(
        """
        SELECT id, judul, pengarang, kategori, penerbit, tahun_terbit, rak, stok, deskripsi
        FROM buku_buku
        WHERE stok > 0
        ORDER BY id
        """
    )
    return render(request, 'peminjaman/tambah-peminjaman.html', {
        'siswa_list': siswa_list,
        'buku_list': buku_list,
    })


def peminjaman_ubah_status(request, pk):
    peminjaman = fetch_one(
        """
        SELECT id, siswa_id, buku_id, tanggal_pinjam, jatuh_tempo,
               keperluan, catatan, status
        FROM buku_peminjaman
        WHERE id = %s
        """,
        [pk],
    )
    if peminjaman is None:
        raise Http404

    if request.method == 'POST':
        with transaction.atomic():
            execute_query(
                "UPDATE buku_peminjaman SET status = %s WHERE id = %s",
                ['Dikembalikan', pk],
            )
            execute_query(
                'UPDATE buku_buku SET stok = stok + 1 WHERE id = %s',
                [peminjaman.buku_id],
            )
        return redirect('peminjaman_list')
    return render(request, 'peminjaman/ubah-status.html', {'peminjaman': peminjaman})