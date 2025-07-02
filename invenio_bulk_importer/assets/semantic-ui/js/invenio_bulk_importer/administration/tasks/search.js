// This file is part of InvenioCommunities
// Copyright (C) 2025 Ubiquity Press.
//
// Invenio RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import ReactDOM from "react-dom";
import { BulkImporter } from "@ubiquitypress/react-invenio-bulk-importer";
import "@ubiquitypress/react-invenio-bulk-importer/style.css";

const BulkImporterSearchApp = () => {
  return <BulkImporter.Search />;
};

const initializeBulkImporter = () => {
  const domContainer = document.getElementById("invenio-search-config");

  if (!domContainer) {
    console.error("Could not find element with id 'invenio-search-config'");
    return;
  }

  ReactDOM.render(<BulkImporterSearchApp />, domContainer);
};

initializeBulkImporter();
