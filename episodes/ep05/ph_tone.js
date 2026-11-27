THREE.ShaderChunk.tonemapping_pars_fragment=THREE.ShaderChunk.tonemapping_pars_fragment.replace('vec3 CustomToneMapping( vec3 color ) { return color; }',`vec3 CustomToneMapping( vec3 color ) {
 const mat3 I = mat3( vec3( 0.856627153315983, 0.137318972929847, 0.11189821299995 ), vec3( 0.0951212405381588, 0.761241990602591, 0.0767994186031903 ), vec3( 0.0482516061458583, 0.101439036467562, 0.811302368396859 ) );
 const mat3 O = mat3( vec3( 1.1271005818144368, - 0.1413297634984383, - 0.14132976349843826 ), vec3( - 0.11060664309660323, 1.157823702216272, - 0.11060664309660294 ), vec3( - 0.016493938717834573, - 0.016493938717834257, 1.2519364065950405 ) );
 color *= toneMappingExposure; color = LINEAR_SRGB_TO_LINEAR_REC2020 * color; color = I * color;
 color = clamp( ( log2( max( color, 1e-10 ) ) + 12.47393 ) / 16.499999, 0.0, 1.0 ); color = agxDefaultContrastApprox( color );
 float l = dot( color, vec3( 0.2126, 0.7152, 0.0722 ) ); color = pow( max( color, 0.0 ), vec3( ${L.pow.toFixed(3)} ) ); color = l + ${L.sat.toFixed(3)} * ( color - l );
 color = O * color; color = pow( max( vec3( 0.0 ), color ), vec3( 2.2 ) ); return clamp( LINEAR_REC2020_TO_LINEAR_SRGB * color, 0.0, 1.0 ); }`);
