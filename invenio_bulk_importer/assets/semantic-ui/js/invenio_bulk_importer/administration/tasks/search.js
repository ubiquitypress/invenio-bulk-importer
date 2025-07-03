// This file is part of InvenioCommunities
// Copyright (C) 2025 Ubiquity Press.
//
// Invenio RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import { createSearchAppInit, initDefaultSearchComponents } from "@js/invenio_search_ui";
import { SearchBulkActionContext } from "@js/invenio_administration";
import { 
  Button, 
  Modal, 
  Icon, 
  ModalHeader, 
  ModalContent, 
  ModalDescription, 
  ModalActions, 
  Header, 
  Form, 
  FormField, 
  Radio 
} from "semantic-ui-react";

const ImportModal = () => {
  const [open, setOpen] = React.useState(false);
  const [selectedOption, setSelectedOption] = React.useState('csv');

  const handleImport = () => {
    console.log(`Importing with option: ${selectedOption}`);
    setOpen(false);
  };

  return (
    <Modal
      onClose={() => setOpen(false)}
      onOpen={() => setOpen(true)}
      open={open}
      trigger={
        <Button primary>
          <Icon name='upload'/>
          Import
        </Button>
      }
    >
      <ModalHeader>Import Data</ModalHeader>
      <ModalContent>
        <ModalDescription>
          <Header>Select Import Type</Header>
          <Form>
            <FormField>
              <Radio
                label='Import from CSV'
                name='importType'
                value='csv'
                checked={selectedOption === 'csv'}
                onChange={(e, { value }) => setSelectedOption(value)}
              />
            </FormField>
            <FormField>
              <Radio
                label='Import from JSON'
                name='importType'
                value='json'
                checked={selectedOption === 'json'}
                onChange={(e, { value }) => setSelectedOption(value)}
              />
            </FormField>
            <FormField>
              <Radio
                label='Import from API'
                name='importType'
                value='api'
                checked={selectedOption === 'api'}
                onChange={(e, { value }) => setSelectedOption(value)}
              />
            </FormField>
          </Form>
        </ModalDescription>
      </ModalContent>
      <ModalActions>
        <Button onClick={() => setOpen(false)}>
          Cancel
        </Button>
        <Button positive onClick={handleImport}>
          <Icon name='checkmark' />
          Import
        </Button>
      </ModalActions>
    </Modal>
  );
};

const CustomSearchBarContainer = ({ children, ...props }) => {
  const { relaxed, padded, ...cleanProps } = props;
  
  return (
    <div {...cleanProps}>
      <div style={{ marginBottom: '1rem' }}>
        <ImportModal />
      </div>
      {children}
    </div>
  );
};

const initializeSearch = () => {
  const domContainer = document.getElementById("invenio-search-config");

  if (!domContainer) {
    console.error("Could not find element with id 'invenio-search-config'");
    return;
  }

  const customComponents = {
    "SearchApp.searchbarContainer": CustomSearchBarContainer,
  };


  try {
    if (initDefaultSearchComponents) {
      try {
        const defaultComponents = initDefaultSearchComponents(domContainer);
        
        // Merge default with custom components
        const allComponents = {
          ...defaultComponents,
          ...customComponents,
        };

        createSearchAppInit(
          allComponents,
          true,
          "invenio-search-config",
          false,
          SearchBulkActionContext
        );
        
        console.log("Search initialized with default + custom components");
        return;
      } catch (error) {
        console.warn("Could not initialize default components, using custom only:", error);
      }
    }
  } catch (importError) {
    console.warn("Could not import initDefaultSearchComponents:", importError);
  }

  // Fallback: Initialize with just our custom components
  createSearchAppInit(
    customComponents,
    true,
    "invenio-search-config",
    false,
    SearchBulkActionContext
  );
  
  console.log("Search initialized with custom components only");
};

initializeSearch();