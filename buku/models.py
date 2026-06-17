from django.db import models

class Buku(models.Model):
    judul = models.CharField(max_length=200)
    pengarang = models.CharField(max_length=100)
    kategori = models.CharField(max_length=50)
    penerbit = models.CharField(max_length=100)
    tahun_terbit = models.IntegerField()
    rak = models.CharField(max_length=20)
    stok = models.IntegerField()
    deskripsi = models.TextField(blank=True)

    def __str__(self):
        return self.judul

class Siswa(models.Model):
    nama = models.CharField(max_length=100)
    kelas = models.CharField(max_length=50)
    nis = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.nama

class Peminjaman(models.Model):
    siswa = models.ForeignKey(Siswa, on_delete=models.CASCADE, related_name='peminjaman')
    buku = models.ForeignKey(Buku, on_delete=models.CASCADE)
    tanggal_pinjam = models.DateField()
    jatuh_tempo = models.DateField()
    keperluan = models.TextField(blank=True)
    catatan = models.TextField(blank=True)
    status = models.CharField(max_length=20, default='Dipinjam')

    def __str__(self):
        return f"{self.siswa.nama} meminjam {self.buku.judul}"