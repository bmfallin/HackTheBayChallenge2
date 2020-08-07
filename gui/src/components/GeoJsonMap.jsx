import axios from "axios";
import React from 'react';
import { Viewer } from 'resium';
import { GeoJsonDataSource } from "resium";

export default function GeoJsonMap(props) {

    const [json, setJson] = React.useState(null);

    React.useEffect(() => {
        axios.get(props.url)
        .then(res => {
            setJson(res.data);
        })
        .catch(err => {
            console.log(err);
        })
    }, []);

    return (
        <Viewer full>
          <GeoJsonDataSource data={json} />
        </Viewer>
    );
}