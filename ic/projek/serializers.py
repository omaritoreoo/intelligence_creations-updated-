# projek/serializers.py
from rest_framework import serializers
from .models import Project, IntelligenceEngineering, ProblemFraming, DatasetRequest, DataProcessing, TrainingModel, DatasetReply
from django.contrib.auth.models import User # Untuk serializer user jika diperlukan


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['username'] # Biasanya username tidak bisa diubah lewat API ini


class ProjectSerializer(serializers.ModelSerializer):
    supervisor = UserSerializer(read_only=True) # Menampilkan detail supervisor, read-only
    supervisor_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='supervisor', write_only=True, required=False, allow_null=True
    ) # Untuk menerima ID supervisor saat create/update

    class Meta:
        model = Project
        fields = '__all__' # Atau daftar field yang ingin Anda ekspos
        read_only_fields = ['created_at', 'updated_at']


class IntelligenceEngineeringSerializer(serializers.ModelSerializer):
    project_detail = ProjectSerializer(source='project', read_only=True) # Untuk menampilkan detail project terkait
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), write_only=True
    ) # Untuk menerima project_id saat create/update

    class Meta:
        model = IntelligenceEngineering
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class ProblemFramingSerializer(serializers.ModelSerializer):
    project_detail = ProjectSerializer(source='project', read_only=True)
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), write_only=True
    )
    framed_by_detail = UserSerializer(source='framed_by', read_only=True)
    framed_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='framed_by', write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = ProblemFraming
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class DatasetRequestSerializer(serializers.ModelSerializer):
    project_detail = ProjectSerializer(source='project', read_only=True)
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), write_only=True
    )
    requested_by_detail = UserSerializer(source='requested_by', read_only=True)
    requested_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='requested_by', write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = DatasetRequest
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class DataProcessingSerializer(serializers.ModelSerializer):
    project_detail = ProjectSerializer(source='project', read_only=True)
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), write_only=True
    )
    processed_by_detail = UserSerializer(source='processed_by', read_only=True)
    processed_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='processed_by', write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = DataProcessing
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class TrainingModelSerializer(serializers.ModelSerializer):
    project_detail = ProjectSerializer(source='project', read_only=True)
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), write_only=True
    )
    training_data_used_detail = DataProcessingSerializer(source='training_data_used', read_only=True)
    training_data_used_id = serializers.PrimaryKeyRelatedField(
        queryset=DataProcessing.objects.all(), source='training_data_used', write_only=True, required=False, allow_null=True
    )
    trained_by_detail = UserSerializer(source='trained_by', read_only=True)
    trained_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='trained_by', write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = TrainingModel
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'training_date']

class DatasetReplySerializer(serializers.ModelSerializer):
    project_detail = ProjectSerializer(source='project', read_only=True)
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), write_only=True
    )

    dataset_request_detail = DatasetRequestSerializer(source='dataset_request', read_only=True)
    dataset_request = serializers.PrimaryKeyRelatedField(
        queryset=DatasetRequest.objects.all(), write_only=True, required=False, allow_null=True
    )

    received_by_detail = UserSerializer(source='received_by', read_only=True)
    received_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='received_by', write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = DatasetReply
        fields = '__all__' # Expose all fields from the DatasetReply model
        read_only_fields = ['created_at', 'updated_at'] # These fields are auto-managed by Django
