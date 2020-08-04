import axios from "axios";
import React from 'react';
import { Viewer } from 'resium';
import { CzmlDataSource } from "resium";

export default function CzmlMap(props) {

    const [czml, setCzml] = React.useState(null);

    React.useEffect(() => {
        axios.get(props.url)
        .then(res => {
            setCzml(res.data);
        })
        .catch(err => {
            console.log(err);
        })
    }, []);

    return (
        <Viewer full>
          <CzmlDataSource data={czml} />
        </Viewer>
    );
}