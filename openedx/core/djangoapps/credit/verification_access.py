"""
Apply in-course reverification access rules to a course.

We model the rules as a set of user partitions, one for each
verification checkpoint in a course.

For example, suppose that a course has two verification checkpoints,
one at midterm A and one at the midterm B.

Then the user partitions would look like this:

Midterm A:  |-- ALLOW --|-- DENY --|
Midterm B:  |-- ALLOW --|-- DENY --|

where the groups are defined as:

* ALLOW: TODO

* DENY: TODO

"""
from util.db import generate_int_id
from openedx.core.djangoapps.credit.utils import get_course_blocks
from xmodule.modulestore.django import modulestore
from xmodule.modulestore import ModuleStoreEnum
from xmodule.partitions.partitions import Group, UserPartition, NoSuchUserPartitionError


VERIFICATION_SCHEME_NAME = "verification"
VERIFICATION_BLOCK_CATEGORY = "edx-reverification-block"


def apply_verification_access_rules(course_key):
    """
    TODO
    """
    # Retrieve all in-course reverification blocks in the course
    icrv_blocks = get_course_blocks(course_key, VERIFICATION_BLOCK_CATEGORY)

    # Batch all the write queries we're about to do and suppress
    # the "publish" signal to avoid an infinite call loop.
    with modulestore().bulk_operations(course_key, emit_signals=False):

        # Update the verification definitions in the course descriptor
        # This will also clean out old verification partitions if checkpoints
        # have been deleted.
        _set_verification_partitions(course_key, icrv_blocks)


def _unique_partition_id(course):
    """TODO """
    # Exclude all previously used IDs, even for partitions that have been disabled
    # (e.g. if the course author deleted an in-course reverifification block but
    # there are courseware components that reference the disabled partition).
    used_ids = set(p.id for p in course.user_partitions)
    return generate_int_id(used_ids=used_ids)


def _other_partitions(all_partitions, exclude_partitions):
    """todo """
    results = []
    partition_by_id = {
        p.id: p for p in all_partitions
    }

    for pid in set(p.id for p in all_partitions) - set(p.id for p in exclude_partitions):
        partition = partition_by_id[pid]

        # TODO -- explain
        # TODO -- logging
        if partition.scheme.name == VERIFICATION_SCHEME_NAME:
            results.append(
                UserPartition(
                    id=partition.id,
                    name=partition.name,
                    description=partition.description,
                    scheme=partition.scheme,
                    parameters=partition.parameters,
                    groups=partition.groups,
                    active=False,
                )
            )

        # TODO -- explain
        # TODO -- logging
        else:
            results.append(partition)

    return results


def _set_verification_partitions(course_key, icrv_blocks):
    """TODO """
    scheme = UserPartition.get_scheme(VERIFICATION_SCHEME_NAME)
    if scheme is None:
        # TODO -- log an error here
        return []

    course = modulestore().get_course(course_key)
    if course is None:
        # TODO: log an error here
        return []

    partition_id_for_location = {
        p.parameters["location"]: p.id
        for p in course.user_partitions
        if p.scheme == scheme and "location" in p.parameters
    }

    partitions = [
        UserPartition(
            id=partition_id_for_location.get(
                unicode(block.location),
                _unique_partition_id(course)
            ),
            name=block.related_assessment,
            description=u"Verification Checkpoint",  # TODO: add anything else here?
            scheme=scheme,
            parameters={"location": unicode(block.location)},
            groups=[
                Group(scheme.ALLOW, "Allow access to content"),
                Group(scheme.DENY, "Deny access to content"),
            ]
        )
        for block in icrv_blocks
    ]

    # Preserve existing, non-verified partitions from the course
    # Mark partitions for deleted in-course reverification as disabled.
    course.user_partitions = partitions + _other_partitions(course.user_partitions, partitions)
    modulestore().update_item(course, ModuleStoreEnum.UserID.system)

    return partitions
