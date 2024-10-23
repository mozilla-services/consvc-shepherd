"""Serializers for the json API that drives the ad-ops-dashboard"""

from rest_framework import serializers

from consvc_shepherd.models import BoostrDeal, BoostrProduct, Campaign, Flight


class BoostrProductSerializer(serializers.ModelSerializer):
    """Turns BoostrProduct in-memory objects into json string"""

    class Meta:
        """Metadata to specify the way BoostrProduct is serialized"""

        model = BoostrProduct
        fields = "__all__"


class CampaignSerializer(serializers.ModelSerializer):
    """Serializer for Campaign model"""

    campaign_fields = serializers.ListSerializer(
        child=serializers.DictField(), write_only=True
    )
    kevel_flight_id = serializers.IntegerField(write_only=True, allow_null=True)

    class Meta:
        """Metadata to specify the way Campaign is serialized"""

        model = Campaign
        fields = "__all__"

    # To do: This code will be updated once we have the UI to assign multiple flights to a campaign.
    def get_kevel_flight_id(self, obj):
        """Retrieve the most recent flight ID related to the campaign."""
        flight = obj.flights.last()
        return flight.kevel_flight_id if flight else None

    def validate(self, data):
        """Validate campaign data, ensuring the deal exists and total net spend matches the deal amount."""
        deal = data.get("deal")
        if deal is None:
            raise serializers.ValidationError("Deal must be provided.")

        try:
            deal_data = BoostrDeal.objects.get(id=deal.id)
            deal_amount = deal_data.amount
        except BoostrDeal.DoesNotExist as exec:
            raise serializers.ValidationError(
                f"Deal with id {deal.id} does not exist."
            ) from exec

        campaign_fields_data = data.get("campaign_fields", [])
        total_net_spend = sum(
            field.get("net_spend", 0) for field in campaign_fields_data
        ) + data.get("net_spend", 0)

        if total_net_spend != deal_amount:
            raise serializers.ValidationError(
                f"Total net spend ({total_net_spend}) from campaigns must equal the deal amount ({deal_amount})."
            )

        return data

    def create(self, validated_data):
        """Create a new campaign and update existing campaign fields based on validated data."""
        kevel_flight_id = validated_data.pop("kevel_flight_id", None)
        campaign_fields_data = validated_data.pop("campaign_fields", [])
        campaign = Campaign.objects.create(**validated_data)

        self._update_existing_campaigns(campaign_fields_data)

        if kevel_flight_id is not None:
            Flight.objects.create(campaign=campaign, kevel_flight_id=kevel_flight_id)

        return campaign

    def update(self, instance, validated_data):
        """Update an existing campaign."""
        campaign_fields_data = validated_data.pop("campaign_fields", [])
        kevel_flight_id = validated_data.pop("kevel_flight_id", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if kevel_flight_id is None:
            instance.flights.all().delete()
        else:
            Flight.objects.update_or_create(
                campaign=instance, defaults={"kevel_flight_id": kevel_flight_id}
            )

        self._update_existing_campaigns(campaign_fields_data)

        return instance

    def _update_existing_campaigns(self, campaign_fields_data):
        """Update existing campaigns based on the provided data."""
        for field_data in campaign_fields_data:
            campaign_id = field_data.get("campaign_id")
            if campaign_id is not None:
                try:
                    existing_campaign = Campaign.objects.get(id=campaign_id)
                    existing_campaign.impressions_sold = field_data.get(
                        "impressions_sold", existing_campaign.impressions_sold
                    )
                    existing_campaign.net_spend = field_data.get(
                        "net_spend", existing_campaign.net_spend
                    )
                    existing_campaign.save()
                except Campaign.DoesNotExist:
                    continue

    def to_representation(self, instance):
        """Customize the representation to include kevel_flight_id."""
        representation = super().to_representation(instance)
        representation["kevel_flight_id"] = self.get_kevel_flight_id(instance)
        return representation


class BoostrDealSerializer(serializers.ModelSerializer):
    """Serializer for BoostrDeal model"""

    class Meta:
        """Metadata for BoostrDealSerializer"""

        model = BoostrDeal
        fields = ["id", "name"]


class NestedCampaignSerializer(serializers.Serializer):
    """Serializer for individual campaign data."""

    id = serializers.IntegerField(required=False)
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    ad_ops_person = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    kevel_flight_id = serializers.IntegerField(required=False, allow_null=True)
    impressions_sold = serializers.IntegerField()
    net_spend = serializers.IntegerField()
    deal = serializers.IntegerField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    seller = serializers.CharField()


class SplitCampaignSerializer(serializers.Serializer):
    """Serializer for Split create/update of campaigns."""

    campaigns = NestedCampaignSerializer(many=True, write_only=True)
    deal = serializers.IntegerField(write_only=True)

    def validate(self, data: dict) -> dict:
        """Validate campaign data."""
        campaigns = data.get("campaigns", [])

        if not campaigns:
            raise serializers.ValidationError("No campaign data was provided.")

        deal_id = data.get("deal")

        try:
            parent_campaign_id = campaigns[0].get("id")
            parent_campaign_instance = Campaign.objects.get(id=parent_campaign_id)
            campaign_net_spend = parent_campaign_instance.net_spend
            campaign_impression_sold = parent_campaign_instance.impressions_sold
        except Campaign.DoesNotExist:
            raise serializers.ValidationError("Campaign does not exist.")

        try:
            deal = BoostrDeal.objects.get(id=deal_id)
        except BoostrDeal.DoesNotExist:
            raise serializers.ValidationError(f"Deal with ID {deal_id} does not exist.")

        total_net_spend = sum(field.get("net_spend", 0) for field in campaigns)
        total_impression_sold = sum(
            field.get("impressions_sold", 0) for field in campaigns
        )

        if total_net_spend != campaign_net_spend:
            raise serializers.ValidationError(
                f"Total net spend ({total_net_spend}) must equal "
                f"the parent campaign's net spend ({campaign_net_spend})."
            )

        if (
            campaign_impression_sold
            and campaign_impression_sold > 0
            and total_impression_sold != campaign_impression_sold
        ):
            raise serializers.ValidationError(
                f"Total impression sold ({total_impression_sold}) must equal "
                f"the parent campaign's impression sold ({campaign_impression_sold})."
            )

        data["deal_instance"] = deal
        return data

    def create(self, validated_data: dict) -> list:
        """Create new campaigns and update existing ones."""
        campaigns = validated_data.pop("campaigns", [])
        deal = validated_data.pop("deal_instance")

        created_campaigns = []
        for campaign in campaigns:
            campaign_id = campaign.get("id")
            if campaign_id:
                created_campaigns.append(
                    self._update_existing_campaign(campaign_id, campaign, deal)
                )
            else:
                created_campaigns.append(self._create_new_campaign(campaign, deal))

        return created_campaigns

    def _update_existing_campaign(
        self, campaign_id: int, campaign: dict, deal
    ) -> Campaign:
        """Update an existing campaign."""
        try:
            kevel_flight_id = campaign.pop("kevel_flight_id", None)
            existing_campaign = Campaign.objects.get(id=campaign_id)
            if kevel_flight_id is None:
                Flight.objects.filter(campaign=campaign_id).delete()
            else:
                self._create_or_update_flight(existing_campaign, kevel_flight_id)

        except Campaign.DoesNotExist:
            raise serializers.ValidationError(
                f"Campaign with ID {campaign_id} does not exist."
            )

        for attr, value in campaign.items():
            if attr != "id":
                setattr(existing_campaign, attr, deal if attr == "deal" else value)

        existing_campaign.save()
        return existing_campaign

    def _create_new_campaign(self, campaign: dict, deal) -> Campaign:
        """Create a new campaign."""
        kevel_flight_id = campaign.pop("kevel_flight_id", None)
        campaign["deal"] = deal
        new_campaign = Campaign.objects.create(**campaign)
        self._create_or_update_flight(new_campaign, kevel_flight_id)
        return new_campaign

    def _create_or_update_flight(self, campaign: Campaign, kevel_flight_id: int):
        """Create or update flight id for campaign."""
        if kevel_flight_id is not None:
            Flight.objects.update_or_create(
                campaign=campaign, defaults={"kevel_flight_id": kevel_flight_id}
            )
