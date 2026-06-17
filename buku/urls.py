from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # Jalur untuk Buku
    path('buku/', views.buku_list, name='buku_list'),
    path('buku/tambah/', views.buku_tambah, name='buku_tambah'),
    path('buku/detail/<int:pk>/', views.buku_detail, name='buku_detail'), # Diubah menjadi pk
    path('buku/edit/<int:pk>/', views.buku_edit, name='buku_edit'),     # Diubah menjadi pk
    path('buku/delete/<int:pk>/', views.buku_delete, name='buku_delete'), # Diubah menjadi pk

    # Jalur untuk Peminjaman
    path('peminjaman/', views.peminjaman_list, name='peminjaman_list'),
    path('peminjaman/tambah/', views.peminjaman_tambah, name='peminjaman_tambah'),
    path('peminjaman/ubah-status/<int:pk>/', views.peminjaman_ubah_status, name='peminjaman_ubah_status'), # Disamakan nama fungsi & pk

    # Jalur untuk Siswa/User
    path('siswa/', views.siswa_list, name='siswa_list'),
    path('siswa/tambah/', views.siswa_tambah, name='siswa_tambah'),
    path('siswa/detail/<int:pk>/', views.siswa_detail, name='siswa_detail'), # Diubah menjadi pk
    path('siswa/edit/<int:pk>/', views.siswa_edit, name='siswa_edit'),     # Diubah menjadi pk
    path('siswa/hapus/<int:pk>/', views.siswa_hapus, name='siswa_hapus'),   # Diubah menjadi pk
]