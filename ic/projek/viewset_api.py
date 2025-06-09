# projek/viewset_api.py
from rest_framework import viewsets, permissions
from .models import Project, IntelligenceEngineering, ProblemFraming, DatasetRequest, DataProcessing, TrainingModel
from .serializers import (
    ProjectSerializer, IntelligenceEngineeringSerializer, ProblemFramingSerializer,
    DatasetRequestSerializer, DataProcessingSerializer, TrainingModelSerializer
)


# Contoh ViewSet dasar. Anda bisa menyesuaikan permissions dan querysets
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # Contoh permission: bisa dilihat semua, tapi hanya authenticated user yang bisa mengubah

    def perform_create(self, serializer):
        # Jika Anda ingin secara otomatis mengatur supervisor ke user yang sedang login saat membuat proyek baru
        serializer.save(supervisor=self.request.user)

    def perform_update(self, serializer):
        # Pastikan supervisor tidak diubah jika tidak ada input eksplisit
        if 'supervisor_id' not in self.request.data:
            serializer.save()
        else:
            serializer.save(supervisor=self.request.user if self.request.data['supervisor_id'] is None else None)


class IntelligenceEngineeringViewSet(viewsets.ModelViewSet):
    queryset = IntelligenceEngineering.objects.all()
    serializer_class = IntelligenceEngineeringSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Contoh: Jika Anda ingin proyek harus diisi saat pembuatan IntelligenceEngineering
        if 'project' not in self.request.data:
            raise serializers.ValidationError({"project": "Project ID is required."})
        serializer.save()


class ProblemFramingViewSet(viewsets.ModelViewSet):
    queryset = ProblemFraming.objects.all()
    serializer_class = ProblemFramingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Contoh: Otomatis mengisi framed_by dengan user yang sedang login
        serializer.save(framed_by=self.request.user)


class DatasetRequestViewSet(viewsets.ModelViewSet):
    queryset = DatasetRequest.objects.all()
    serializer_class = DatasetRequestSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Contoh: Otomatis mengisi requested_by dengan user yang sedang login
        serializer.save(requested_by=self.request.user)


class DataProcessingViewSet(viewsets.ModelViewSet):
    queryset = DataProcessing.objects.all()
    serializer_class = DataProcessingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Contoh: Otomatis mengisi processed_by dengan user yang sedang login
        serializer.save(processed_by=self.request.user)


class TrainingModelViewSet(viewsets.ModelViewSet):
    queryset = TrainingModel.objects.all()
    serializer_class = TrainingModelSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Contoh: Otomatis mengisi trained_by dengan user yang sedang login
        serializer.save(trained_by=self.request.user)