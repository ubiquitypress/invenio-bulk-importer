# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Ubiquity Press.
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Fixtures for testing Invenio RDM Record resources."""

import pytest
from invenio_files_rest.models import Bucket, ObjectVersion
from invenio_rdm_records.proxies import current_rdm_records_service as record_service
from invenio_rdm_records.records.api import RDMDraft, RDMRecord

from invenio_bulk_importer.record_types.rdm import RDMRecord as BulkImportRDMRecord


@pytest.fixture
def bucket_with_object_version(db, location):
    """Create a bucket and objectversion."""
    b1 = Bucket.create(location=location)
    with open("README.rst", "rb") as fp:
        ObjectVersion.create(b1, "README.rst", stream=fp)
    db.session.commit()

    # Check if the file exists in the bucket
    object_versions = ObjectVersion.get_by_bucket(b1.id)
    assert object_versions.count() == 1
    assert object_versions[0].key == "README.rst"

    return b1


@pytest.fixture
def validated_rdm_record_instance_with_community(valid_importer_record_with_community):
    """Fixture to create an RDMRecord instance, with community."""
    rdm_record = BulkImportRDMRecord(
        (
            None,
            None,
        ),
        importer_record=valid_importer_record_with_community._obj,
    )
    return rdm_record


@pytest.fixture
def validated_rdm_record_instance_no_files(valid_importer_record_no_files):
    """Fixture to create an RDMRecord instance."""
    rdm_record = BulkImportRDMRecord(
        (
            None,
            None,
        ),
        importer_record=valid_importer_record_no_files._obj,
    )
    return rdm_record


@pytest.fixture
def validated_rdm_record_instance(valid_importer_record):
    """Fixture to create an RDMRecord instance."""
    rdm_record = BulkImportRDMRecord(
        (
            None,
            None,
        ),
        importer_record=valid_importer_record._obj,
    )
    return rdm_record


@pytest.fixture
def serialized_record():
    """Fixture to create a serialized record."""
    return {
        "pids": {
            "doi": {"identifier": "10.5281/zenodo.10572732", "provider": "external"}
        },
        "default_community": "test-community",
        "communities": ["test-community"],
        "files": [
            "README.rst",
            "s3://service-rua/up/core/fixtures/key_help.json",
            "gs://rua-uplo/files/books/1/13c3fea3-ac2f-4c9c-a71f-b59956f3ac10.pdf",
            "https://www.w3.org/2001/03/xml.xsd",
        ],
        "access": {
            "record": "public",
            "files": "restricted",
            "embargo": {"active": "TRUE", "until": "2120-10-06", "reason": "espionage"},
        },
        "custom_fields": {
            "imprint:imprint": {
                "isbn": "978-3-16-148410-0",
                "pages": "15-23",
                "edition": "23rd",
                "place": "Whoville",
                "volume": "3",
            }
        },
        "metadata": {
            "title": "Micraster ernsti Schlüter 2024, sp. nov.",
            "additional_titles": [
                {
                    "title": "Something else",
                    "type": {"id": "alternative-title"},
                    "lang": {"id": "eng"},
                }
            ],
            "publication_date": "2024-01-18",
            "description": "<i>Micraster ernsti</i> sp. nov.   <p>(Figs. 2&ndash;5)</p>  <p> ? 1954 <i>Micraster</i> (<i>Isomicraster</i>) <i>senonensis</i> Lambert; Kermack, pl. 24, fig. 13; pl. 25, fig. 15; pl. 26, fig. 17.</p>   <p> 1972 <i>Micraster</i> (<i>Gibbaster</i>) sp.; Ernst, figs. 4, 2a; pl. 18, fig. 3&ndash;4.</p>   <p> 1989 <i>Gibbaster</i> sp.; Frerichs, p.161, fig. 6.</p>   <p> pars 2012 <i>Micraster stolleyi</i> Lambert; Smith &amp; Wright, p. 683, text-fig. 303; pl. 247, figs. 1&ndash;7.</p>   <p> 2023 <i>Micraster</i> sp.; Schl&uuml;ter &amp; Schneider, p. 57, fig. 60.</p>   <p> <b>Diagnosis.</b> Conical lateral profile with a polygonate outline; apical disc subcentral, periproct well below mid-height of the test. Generally slender labral plate with a smooth rim at its tip, largely covering the peristome. Peristome faces forward; the oral surface surrounding the peristome is slightly depressed. The peristome is relatively far away from the anterior margin (mean=20% of the test length): the periplastronal plates have a granular-mammilate surface; the perradial area in the plates of the petals is inflated. The anterior ambulacrum has aborally elongated pore pairs.</p>   <p> <b>Types.</b> Holotype is MB.E.8577 from the <i>Echinocorys conica</i> / <i>Galeola pappilosa</i> Zone, lower Campanian from the quarry adjacent to H&ouml;ver, southeast of Hannover, Lower Saxony, Germany; paratypes are MB.E.8583 <i>conica</i> / <i>pappilosa</i> Zone, Teutonia Nord quarry, Hannover, and MB.E.8576, <i>conica</i> / <i>pappilosa</i> Zone, lower Campanian, H&ouml;ver.</p>   <p> <b>Derivatio nominis.</b> In honour of the late Gundolf Ernst, who contributed tremendously with his work to the knowledge of the evolution of the genus <i>Micraster</i>.</p>   <p> <b>Stratum typicum.</b> From the <i>conica</i> / <i>pappilosa</i> Zone, lower Campanian.</p>   <p> <b>Locus typicus.</b> The area southeast of Hannover, Lower Saxony, Germany, i.e. the working limestone quarries in Hannover-Misburg, Teutonia Nord and Germania IV, as well as the quarry in H&ouml;ver in the vicinity of Hannover, Lower Saxony, Germany.</p>   <p> <b>Additional material.</b> MB.E:8574, 8575 (ex leg. Duckstein), MB.E.8576, 8578, 8579, MB.E.8580, MB.E.8581&ndash; 8582 from the lower Campanian of H&ouml;ver, vicinity of Hannover, Lower Saxony, Germany.</p>   <p> <b>Description.</b> Cordiform and polygonate (more pronounced in larger specimens) in outline. The test is slightly wider than long (length/width ratio of the tests ranges from 1.00 to 1.07, mean=1.02, n=10). The tests have a somewhat conical lateral profile, rather rounded towards the apex. Specimen MB.E.8583 is clearly more conical in profile, tapering towards the apex. The test is highest approximately a bit posterior from the apical disc which has a slightly elongated outline (Fig. 5B). It is ethmophract, having four gonopores and an enlarged madreporite; the posterior genital plates are not separated by the madreporite (Fig. 5C). The apical disc is in a subcentral position, somewhat anterior to the mid-length of the test, ranging from 34 to 44% of the test length (mean=40%, n=7) from the test length (measured from the anterior edge of ocular plate III).</p>   <p>The little sunken paired petals have conjugate anisopores with outer elongated pores. The perradius of the petals is weakly inflated (see Rowe, 1899; Olszewska-Neijbert, 2007; Fig. 4B) with a shallow granular ridge adapically of the pore pairs. The anterior paired petals have a straight outline and bear 75 pore pairs per column at a length of 64 mm and the posterior petals bear 68 pore pairs per column at the same test length. The outline of the posterior paired petals is straight and only very slightly curved close to the apical disc. The anterior paired petals diverge with an angle of 122&ndash;150&deg; (mean=130&deg;, n=7), whereas the posterior paired petals diverge with an angle of 52&ndash;64&deg; (mean=57&deg;, n=6) (both measured in plan view from photos).</p>  <p>Ambitally, ambulacrum III forms a very shallow anterior notch which leads adorally as a little depressed groove towards the faintly sunken peristome. Aborally, AIII is only very slightly sunken in an adapical direction where it shows conjugate anisopores with slightly more elongated outer pores. The surface of the ambulacrum III is granular and plating sutures are easily visible.</p>  <p>The amphisternous plastron has symmetrical (Fig. 5A) to asymmetrical sternal plates in specimen MB.E.8576 (Fig. 5B); in the latter case, the contact of the sternals to the labrum is convex, rather than concave (Fig. 5B) and their length is 46% of the test length (43&ndash;51%, n=8).</p>  <p>The shape of the labral plate is slender with almost parallel sides (Fig. 5A). The labral plate is relatively short, equal to 10% of the test length (range: 7&ndash;13%, n=8). The tip of the labrum has a prominent smooth rim. The labrum is projecting and covers completely the peristome or in such a way that only a small part of the peristomal opening can be seen from the oral view. The second ambulacral plates (I.a.2 and I.b.2) adjacent to the labrum are relatively long, extending beyond the back of the labrum by about one-third of their length. The peristome is located in a slight depression and is obliquely facing forward. Its anterior margin is at a distance of 17&ndash;23% of the test length to the anterior edge of the test (mean=20%, n=9). Moderately-developed phyllodes comprise 4&ndash;6 enlarged isopores with a prominent interporal knob in ambulacrum II; III and IV, with smaller-sized pore pairs in ambulacrum I and V. Interambulacrum 2 and 3 are disjunct from the peristomal opening. Interambulacrum 1 and 5 on the oral surface are amphiplacous.</p>  <p> The periplastronal ambulacral plates reveal scattered tubercles surrounded by a granular-mammilate surface (Fig. 4D). The upper surface has densely arranged granules with sparse small tubercles. Aligned granules can be seen shortly above the oral surface from the distal ends of the paired petals to the ambitus, resembling parafascioles (<i>sensu</i> N&eacute;raudeau <i>et al.</i>, 1998); such parafascioles can be also found at the lower third of the junction of the interambulacral plates (interradius) in interambulacrum 1 and 4.</p>   <p>The adapical edge of the periproct is 37&ndash;49% of the test height (mean=43%, n=8).</p>  <p>In contrast, no traces of a subanal fasciole were found in any specimen and the posterior face is truncated and almost vertical.</p>  <p> <b>Remarks.</b> <i>Micraster</i> species with a more inflated and conical shape, a low-positioned periproct and subpetaloid anterior ambulacra were traditionally referred to as the subgenus <i>Gibbaster</i> (Gauthier, 1888). Stokes (1975) and Schl&uuml;ter <i>et al.</i> (2023) declined to further subdivide <i>Micraster</i> into <i>Gibbaster</i> and consider <i>Gibbaster</i> to be synonymous with <i>Micraster</i> due to the polyphyletic development in the shape of the test. In addition, the subpetaloid development in ambulacrum III can also occur in specimens which would be commonly addressed as <i>Micraster</i>. Further, Schl&uuml;ter <i>et al.</i> (2023) found that the subpetaloid development in ambulacrum III and the degree of the test inflation can vary dramatically within species from the Santonian of northern Cantabria, Spain. In particular, in <i>Micraster mengaudi</i> (Lambert 1920a) and <i>Micraster quebrada</i>, intraspecific variation ranges from non-petaloid to sub-petaloid in pore pair development in ambulacrum III, and the test shape can range from rather flat to highly inflated.</p>   <p> Regarding the history of the herein-described species, Ernst (1970b) identified several specimens of what he assumed at this time to be an undescribed species of the genus <i>Gibbaster</i>. These were from sandy, glauconitic marls from different localities in southern western Munsterland, Germany and this material was dated ranging from upper Santonian to early lower Campanian. Judging by the architecture of the oral surface (dimension of the labrum, presence of a smooth rim at its tip, position of the peristome) and the polygonate outline, this material is indistinguishable from the specimens described herein. However, the Munsterland material is flatter in the lateral profile. Ernst also mentioned the absence of a subanal fasciole in the Santonian specimens and the presence of a subanal fasciole in the Campanian specimens.</p>   <p> Differences in test height as well as the development of a subanal fasciole may also have been caused by phenotypic plasticity in response to differences in the sediment (Schl&uuml;ter 2016). Nonetheless, these differences are most likely due to intraspecific variations and are insufficient to address both forms as distinct species. Accordingly, <i>Micraster ernsti</i> <b>sp. nov.</b> can likely be dated back to the upper Santonian, as present in the Munsterland; unfortunately, the material described by Ernst from there could not be traced. Other late Santonian and Campanian <i>Micraster</i> species which also show a subpetaloid ambulacrum III, i.e. <i>Micraster gibbus</i> (Lamarck, 1816) <i>Micraster fastigatus</i> (Gauthier, 1887), <i>Micraster stolleyi</i> (Lambert, 1901), have a more conical, inflated test and a low-positioned periproct, similar to <i>Micraster ernsti</i> <b>sp. nov.</b>, can be easily distinguished by the position of their peristome which is closer to the anterior margin, their more projecting labrum and the granular tip of the labrum. Another very distinctive feature is the polygonal-shaped outline of the test in <i>Micraster ernsti</i> <b>sp. nov.</b> However, Kermack (1954) illustrated a specimen from the Santonian (Northfleet, Kent, UK) closely resembling <i>Micraster ernsti</i> <b>sp. nov.</b> in the outline and the position of the peristome that may belong to <i>Micraster ernsti</i> <b>sp. nov.</b> under the name <i>Micraster</i> (<i>Isomicraster</i>) <i>senonensis</i>. <i>Micraster senonensis</i> is undoubtedly a synonym of <i>Micraster gibbus</i> (see Smith &amp; Wright, 2012). The Campanian <i>Micraster gourdoni</i> Cotteau, 1889 from France also has a subpetaloid ambulacrum III, the type specimen has a somewhat polygonal outline but is very different to the herein described species by the peristome close to the anterior margin, the strongly projecting labrum and the longer posterior petals. The late Santonian <i>Micraster quebrada</i> has a similar position of the peristome, however, is significantly different in the non-projecting labrum and downward-facing peristome. The morphological distinctions between <i>Micraster ernsti</i> <b>sp. nov.</b>, the here-discussed species, and few other (contemporary) species, as well as additional details, are consolidated in Table 1.</p>",
            "additional_descriptions": [
                {"description": "abstract", "type": {"id": "abstract"}},
                {
                    "description": "methods",
                    "type": {"id": "method"},
                    "lang": {"id": "eng"},
                },
                {"description": "notes", "type": {"id": "notes"}},
            ],
            "version": "1.0.1",
            "publisher": "Ubiquity Press",
            "resource_type": {"id": "publication"},
            "languages": [{"id": "eng"}],
            "locations": {
                "features": [
                    {
                        "description": "Big city",
                        "geometry": {
                            "type": "Point",
                            "coordinates": ["38.8951", "-77.0364"],
                        },
                        "place": "Washington",
                    }
                ]
            },
            "creators": [
                {
                    "person_or_org": {
                        "family_name": "Schlüter",
                        "given_name": "Nils",
                        "type": "personal",
                        "identifiers": [
                            {"scheme": "orcid", "identifier": "0000-0002-1825-0097"}
                        ],
                    },
                    "affiliations": [{"name": "Museum für Naturkunde"}],
                },
                {
                    "person_or_org": {
                        "family_name": "John",
                        "given_name": "Smith",
                        "type": "personal",
                        "identifiers": [{"scheme": "gnd", "identifier": "1089945302"}],
                    },
                    "affiliations": [{"name": "CERN"}],
                },
                {
                    "person_or_org": {
                        "name": "Ubiquity Press",
                        "type": "organizational",
                        "identifiers": [],
                    },
                    "affiliations": [],
                },
                {
                    "person_or_org": {
                        "name": "California Institute of Technology",
                        "type": "organizational",
                        "identifiers": [
                            {"scheme": "isni", "identifier": "0000 0001 0706 8890"},
                            {"scheme": "ror", "identifier": "05dxps055"},
                        ],
                    },
                    "affiliations": [],
                },
            ],
            "contributors": [
                {
                    "person_or_org": {
                        "family_name": "Collins",
                        "given_name": "Bob",
                        "type": "personal",
                        "identifiers": [
                            {"scheme": "orcid", "identifier": "0000-0002-1825-0097"},
                            {"scheme": "isni", "identifier": "0000 0001 2146 438X"},
                        ],
                    },
                    "role": {"id": "editor"},
                    "affiliations": [
                        {"name": "Somewhere Press"},
                        {"name": "Everywhere Press"},
                    ],
                }
            ],
            "subjects": [
                {"subject": "custom"},
                {
                    "id": "http://id.nlm.nih.gov/mesh/A-D000007",
                    "subject": "Abdominal Injuries",
                },
            ],
            "references": [
                {
                    "reference": "Rowe, A. W. (1899) An analysis of the genus Micraster, as determined by rigid zonal collecting from the zone of Rhynchonella Cuvieri to that of Micraster cor-anguinum. The Quarterly Journal of the Geological Society of London, 55, 494 - 547. https: // doi. org / 10.1144 / GSL. JGS. 1899.055.01 - 04.34"
                },
                {
                    "reference": "Neraudeau, D., David, B. & Madon, C. (1998) Tuberculation in spatangoid fascioles: Delineating plausible homologies. Lethaia, 31, 323 - 333. https: // doi. org / 10.1111 / j. 1502 - 3931.1998. tb 00522. x"
                },
                {
                    "reference": "Gauthier, V. (1888) Types nouveaux d'Echinides cretaces. Association Francaise pour l'Avancement des Sciences Comptes Rendus, 16, 527 - 534."
                },
                {
                    "reference": "Stokes, R. B. (1975) Royaumes et provinces fauniques du Cretace etablis sur la base d'une etude systematique du genre Micraster. Memoires du Museum national d'Histoire naturelle, Serie C, 31, 1 - 94."
                },
                {
                    "reference": "Lambert, J. (1920 a) Echinides fossiles des environs de Santander recueilis par M. L. Mengaud. Annales de la Societe Linneenne de Lyon, New Series, 67, 1 - 16."
                },
                {
                    "reference": "Ernst, G. (1970 b) Zur Stammesgeschichte und stratigraphischen Bedeutung der Echiniden-Gattung Micraster in der nordwestdeutschen Oberkreide. Mitteilungen aus dem Geologisch-Palaeontologischen Institut der Universitat Hamburg, 39, 117 - 135."
                },
                {
                    "reference": "Schluter, N. (2016) Ecophenotypic variation and developmental instability in the late Cretaceous echinoid Micraster brevis (Irregularia; Spatangoida). PLoS ONE, 11, 1 - 26. https: // doi. org / 10.1371 / journal. pone. 0148341"
                },
                {
                    "reference": "Lamarck, J. - B. M. de (1816) Histoire naturelle des animaux sans vertebres. Tome 2. Verdiere, Paris, 568 pp."
                },
                {
                    "reference": "Gauthier, V. (1887) Echinides. Description des especes de la craie de Reims et de quelques especes nouvelles de l'Aube et de l'Yonne. Bulletin de la Societe des Sciences Historiques et Naturelles de l'Yonne, 41, 367 - 399."
                },
                {
                    "reference": "Lambert, J. (1901) Essai d'une monographie du genre Micraster et notes sur quelques echinites. Errata et addenda. In: Grossouvre, A. (Ed.), Recherches sur la Craie superieur. Memoires du Service de la Carte geologique de France, 23, pp. 957 - 971."
                },
                {
                    "reference": "Kermack, K. A. (1954) A biometrical study of Micraster coranguinum and M. (Isomicraster) senonensis. Philosophical Transactions of the Royal Society of London, Series B 237, 375 - 428. https: // doi. org / 10.1098 / rstb. 1954.0001"
                },
                {
                    "reference": "Smith, A. B. & Wright, C. V. (2012) British Cretaceous echinoids. Part 9, Atelostomata, 2. Spatangoida (2). Monograph of the Palaeontographical Society, 166, 635 - 754. https: // doi. org / 10.1080 / 25761900.2022.12131819"
                },
                {
                    "reference": "Cotteau, G. (1889) Echinides cretaces de Madagascar. Bulletin de la Societe zoologique de France, 14, 87 – 89."
                },
            ],
            "identifiers": [{"scheme": "doi", "identifier": "10.2307/4146128"}],
            "related_identifiers": [
                {
                    "scheme": "doi",
                    "identifier": "10.1080/10509585.2015.1092083",
                    "resource_type": {"id": "publication-article"},
                    "relation_type": {"id": "ispartof"},
                },
                {
                    "scheme": "arxiv",
                    "identifier": "2305.12345",
                    "resource_type": {"id": "publication-article"},
                    "relation_type": {"id": "ispartof"},
                },
                {
                    "scheme": "doi",
                    "identifier": "10.1080/10509585.2015.1092083/987",
                    "resource_type": {"id": "publication-article"},
                    "relation_type": {"id": "ispartof"},
                },
                {
                    "scheme": "doi",
                    "identifier": "10.1080/10509585.2015.1092033",
                    "relation_type": {"id": "issourceof"},
                },
                {
                    "scheme": "arxiv",
                    "identifier": "2305.12345v1",
                    "resource_type": {"id": "image-figure"},
                    "relation_type": {"id": "cites"},
                },
                {
                    "scheme": "doi",
                    "identifier": "10.5281/zenodo.10561542",
                    "resource_type": {"id": "image-figure"},
                    "relation_type": {"id": "cites"},
                },
                {
                    "scheme": "doi",
                    "identifier": "10.5281/zenodo.10561544",
                    "resource_type": {"id": "image-figure"},
                    "relation_type": {"id": "cites"},
                },
                {
                    "scheme": "doi",
                    "identifier": "10.5281/zenodo.10561546",
                    "resource_type": {"id": "image-figure "},
                    "relation_type": {"id": "cites"},
                },
                {
                    "scheme": "arxiv",
                    "identifier": "astro-ph/0703123v2",
                    "resource_type": {"id": "dataset"},
                    "relation_type": {"id": "cites"},
                },
                {
                    "scheme": "doi",
                    "identifier": "10.5281/zenodo.1056154987",
                    "resource_type": {"id": "publication-article"},
                    "relation_type": {"id": "ispartof"},
                },
            ],
            "rights": [
                {"id": "cc0-1.0"},
                {"title": {"en": "New license"}},
            ],
        },
    }


@pytest.fixture
def rdm_record_instance(bucket_with_object_version, serialized_record):
    """Fixture to create an RDMRecord instance."""
    rdm_record = BulkImportRDMRecord(
        (
            serialized_record,
            None,
        ),
        bucket_with_object_version.id,
    )
    return rdm_record


@pytest.fixture()
def minimal_record():
    """Minimal record data as dict coming from the external world."""
    return {
        "pids": {},
        "files": {
            "enabled": False,  # Most tests don't care about files
        },
        "metadata": {
            "creators": [
                {
                    "person_or_org": {
                        "family_name": "Howlett",
                        "given_name": "James",
                        "type": "personal",
                    }
                },
            ],
            "publication_date": "2020-06-01",
            "publisher": "Acme Inc",
            "resource_type": {"id": "dataset"},
            "title": "Logan",
        },
    }


@pytest.fixture()
def record_owner(UserFixture, app, db):
    """Record owner."""
    u = UserFixture(
        email="record_owner@up.up",
        password="record_owner",
    )
    u.create(app, db)
    return u


@pytest.fixture()
def record(running_app, record_owner, minimal_record, app_config):
    """Create record using the minimal record fixture data."""
    r = record_service.create(record_owner.identity, minimal_record)
    r = record_service.publish(record_owner.identity, r.id)

    RDMRecord.index.refresh()

    return r


@pytest.fixture()
def draft(running_app, record_owner, minimal_record):
    """Create record using the minimal record fixture data."""
    r = record_service.create(record_owner.identity, minimal_record)

    RDMDraft.index.refresh()

    return r
