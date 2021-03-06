from rest_framework.decorators import detail_route
from rest_framework import viewsets, mixins, response

from backend import models
from backend import serializers
from backend import permissions


# Create your views here.
class KitViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.RetrieveModelMixin):
    """
    list:
    List all kits the user has access to. A person user has access to all kits it owns,
    whereas a kit user has access only to itself.

    retrieve:
    Return the given kit, if the user has access to it.
    """

    def get_queryset(self):
        """
        Get a queryset of all kits the user has access to.
        """

        user = self.request.user

        if isinstance(user, models.Kit):
            return models.Kit.objects.filter(pk=user.pk)
        else:
            return models.Kit.kits.owned_by(user=user.pk)

    serializer_class = serializers.HyperlinkedKitSerializer

    @detail_route()
    def config(self, request, pk=None):
        qs = self.get_queryset()
        kit_query = qs.filter(pk=pk)
        if not kit_query.exists():
            return response.Response({"detail": "Not found."}, status=404)
        kit = kit_query.get()
        return response.Response(kit.generate_config())


class KitConfigViewSet(viewsets.ViewSet):
    """
    list:
    List the configurations of all kits the user has access to.
    A person user has access to all kits it owns, whereas a kit
    user has access only to itself.
    """

    def get_queryset(self):
        """
        Get a queryset of all kits the user has access to.
        """

        user = self.request.user

        if isinstance(user, models.Kit):
            return models.Kit.objects.filter(pk=user.pk)
        else:
            return models.Kit.kits.owned_by(user=user.pk)

    def list(self, request, format=None):
        qs = self.get_queryset()
        return response.Response([kit.generate_config() for kit in qs.all()])


class ExperimentViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin):
    """
    list:
    List all experiments the user has access to. A person user has access to experiments
    of all kits it owns. A kit user has access to its experiments.

    retrieve:
    Return the given experiment, if the user has access to it.
    """

    def get_queryset(self):
        """
        Get a queryset of all experiments the user has access to.
        """
        user = self.request.user
        if isinstance(user, models.Kit):
            return models.Experiment.objects.filter(kit=user.pk)
        else:
            kits = models.Kit.kits.owned_by(user.pk)
            return models.Experiment.objects.filter(kit__in=kits)

    serializer_class = serializers.HyperlinkedExperimentSerializer


class PeripheralDefinitionViewSet(viewsets.GenericViewSet,
                                  mixins.ListModelMixin,
                                  mixins.RetrieveModelMixin):
    """
    list:
    List all peripheral device definitions.

    retrieve:
    Return the given peripheral device definition.
    """

    def get_queryset(self):
        """
        Get a queryset of all peripheral device definitions.
        """
        return models.PeripheralDefinition.objects.all()

    serializer_class = serializers.HyperlinkedPeripheralDefinitionSerializer


class PeripheralConfigurationDefinitionViewSet(viewsets.GenericViewSet,
                                               mixins.ListModelMixin,
                                               mixins.RetrieveModelMixin):
    """
    list:
    List all peripheral device configuration definitions.

    retrieve:
    Return the given peripheral device configuration definition.
    """

    def get_queryset(self):
        """
        Get a queryset of all peripheral device configuration definitions.
        """
        return models.PeripheralConfigurationDefinition.objects.all()

    serializer_class = serializers.HyperlinkedPeripheralConfigurationDefinitionSerializer


class PeripheralViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin):
    """
    list:
    List all peripheral devices the user has access to. A person user has access to peripheral devices
    of all kits it owns. A kit user has access to its peripheral devices.

    retrieve:
    Return the given peripheral device, if the user has access to it.
    """

    def get_queryset(self):
        """
        Get a queryset of all peripheral devices the user has access to.
        """
        user = self.request.user
        if isinstance(user, models.Kit):
            return models.Peripheral.objects.filter(kit=user.pk)
        else:
            kits = models.Kit.kits.owned_by(user.pk)
            return models.Peripheral.objects.filter(kit__in=kits)

    serializer_class = serializers.HyperlinkedPeripheralSerializer


class MeasurementViewSet(viewsets.GenericViewSet,
                         mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.CreateModelMixin):
    """
    list:
    List all measurements the user has access to. A person user has access to measurements
    of all kits it owns. A kit user has access to its measurements.

    retrieve:
    Return the given measurement, if the user has access to it.

    create:
    Create a measurement. Only kit users can add measurements.
    """

    def get_queryset(self):
        """
        Get a queryset of all measurements the user has access to.
        """
        user = self.request.user
        if isinstance(user, models.Kit):
            return models.Measurement.objects.filter(kit=user.pk)
        else:
            kits = models.Kit.kits.owned_by(user.pk)
            return models.Measurement.objects.filter(kit__in=kits)

    serializer_class = serializers.HyperlinkedMeasurementSerializer
    permission_classes = [permissions.IsNotCreationOrIsAuthenticatedKit, ]

    def perform_create(self, serializer):
        serializer.save(kit=self.request.user)
