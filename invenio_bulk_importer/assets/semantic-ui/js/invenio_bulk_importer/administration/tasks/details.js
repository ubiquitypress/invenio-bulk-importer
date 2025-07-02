// This file is part of InvenioCommunities
// Copyright (C) 2025 Ubiquity Press.
//
// Invenio RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import ReactDOM from "react-dom";
import { BulkImporter } from "@ubiquitypress/react-invenio-bulk-importer";
import "@ubiquitypress/react-invenio-bulk-importer/style.css";

const BulkImporterDetailsApp = ({ taskId }) => {
  return <BulkImporter.TaskDetails taskId={taskId} />;
};

const initializeBulkImporterDetails = () => {
  const domContainer = document.getElementById("invenio-details-config");

  if (!domContainer) {
    console.error("Could not find element with id 'invenio-details-config'");
    return;
  }

  // Extract data from DOM attributes
  const taskId = JSON.parse(domContainer.dataset.pid);

  ReactDOM.render(<BulkImporterDetailsApp taskId={taskId} />, domContainer);
};

initializeBulkImporterDetails();
