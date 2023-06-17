import 'react-bootstrap-typeahead/css/Typeahead.css';
import { Typeahead } from "react-bootstrap-typeahead";
import { useRef, useState } from 'react';
import { Option } from 'react-bootstrap-typeahead/types/types';
import TypeaheadCoreProps from 'react-bootstrap-typeahead/types/core/Typeahead';
import tickersOptions from "./tickers"

export default function SymbolTypeahead() {
    const typeaheadRef = useRef<TypeaheadCoreProps>(null);
    const [selected, setSelected] = useState<Array<Option>>([]);

    function updateSelection(selected: Array<Option>) {
        setSelected(selected);
        if (typeaheadRef != null && typeaheadRef.current != null) {
            typeaheadRef.current.toggleMenu();
        }
    }

    return (
        <Typeahead
            multiple={false}
            id="tickersOptions"
            onChange={updateSelection}
            options={tickersOptions}
            placeholder="Choose a ticker..."
            ref={typeaheadRef}
            selected={selected}

        />
    );
}