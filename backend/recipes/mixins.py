from rest_framework import mixins, viewsets


class RetrieveAndListViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
	pass
