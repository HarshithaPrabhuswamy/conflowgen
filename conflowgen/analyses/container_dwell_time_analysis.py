from __future__ import annotations

import datetime
from typing import Collection, Union

from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.container import Container
from conflowgen.analyses.abstract_analysis import AbstractAnalysis
from conflowgen.tools import hashable


class ContainerDwellTimeAnalysis(AbstractAnalysis):
    """
    This analysis can be run after the synthetic data has been generated.
    The analysis returns a data structure that can be used for generating reports (e.g., in text or as a figure)
    as it is the case with :class:`.ContainerDwellTimeAnalysisReport`.
    """

    @staticmethod
    def get_container_dwell_times(
            container_delivered_by_vehicle_type: Union[str, Collection[ModeOfTransport], ModeOfTransport] = "all",
            container_picked_up_by_vehicle_type: Union[str, Collection[ModeOfTransport], ModeOfTransport] = "all",
            storage_requirement: Union[str, Collection[StorageRequirement], StorageRequirement] = "all"
    ) -> set[datetime.timedelta]:
        """
        The containers are filtered according to the provided vehicle types and storage requirements.
        Then, the time between the arrival of the container in the yard and the departure of the container is
        calculated.

        Args:
            container_delivered_by_vehicle_type: One of
                ``"all"``,
                a collection of :class:`ModeOfTransport` enum values (as a list, set, or similar), or
                a single :class:`ModeOfTransport` enum value.
            container_picked_up_by_vehicle_type: One of
                ``"all"``,
                a collection of :class:`ModeOfTransport` enum values (as a list, set, or similar), or
                a single :class:`ModeOfTransport` enum value.
            storage_requirement: One of
                ``"all"``,
                a collection of :class:`StorageRequirement` enum values (as a list, set, or similar), or
                a single :class:`StorageRequirement` enum value.

        Returns:
            A set of container dwell times.
        """
        container_dwell_times: set[datetime.timedelta] = set()

        selected_containers = Container.select()

        if storage_requirement != "all":
            if hashable(storage_requirement) and storage_requirement in set(StorageRequirement):
                selected_containers = selected_containers.where(
                    Container.storage_requirement == storage_requirement
                )
            else:  # assume it is some kind of collection (list, set, ...)
                selected_containers = selected_containers.where(
                    Container.storage_requirement << storage_requirement
                )

        if container_delivered_by_vehicle_type != "all":
            if hashable(container_delivered_by_vehicle_type) \
                    and container_delivered_by_vehicle_type in set(ModeOfTransport):
                selected_containers = selected_containers.where(
                    Container.delivered_by == container_delivered_by_vehicle_type
                )
            else:  # assume it is some kind of collection (list, set, ...)
                selected_containers = selected_containers.where(
                    Container.delivered_by << container_delivered_by_vehicle_type
                )

        if container_picked_up_by_vehicle_type != "all":
            if hashable(container_picked_up_by_vehicle_type) \
                    and container_picked_up_by_vehicle_type in set(ModeOfTransport):
                selected_containers = selected_containers.where(
                    Container.picked_up_by == container_picked_up_by_vehicle_type
                )
            else:  # assume it is some kind of collection (list, set, ...)
                selected_containers = selected_containers.where(
                    Container.picked_up_by << container_picked_up_by_vehicle_type
                )

        container: Container
        for container in selected_containers:
            container_enters_yard = container.get_arrival_time()
            container_leaves_yard = container.get_departure_time()
            container_dwell_time = container_leaves_yard - container_enters_yard
            container_dwell_times.add(container_dwell_time)

        return container_dwell_times